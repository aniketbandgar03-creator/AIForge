import os
import uuid
import shutil
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.database import db_manager
from app.schemas import ChatRequest, ChatResponse, HistoryItem, DatasetUploadResponse
from app.agent import agent_service

UPLOAD_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_manager.connect()
    yield
    await db_manager.disconnect()


app = FastAPI(
    title="AIForge – Intelligent Assistant & Task Automation API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/datasets/upload", response_model=DatasetUploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .csv files are currently supported.",
        )

    dataset_id = str(uuid.uuid4())[:8]
    save_path = os.path.join(UPLOAD_DIR, f"{dataset_id}_{file.filename}")

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        df = pd.read_csv(save_path)
        columns = df.columns.tolist()
        total_rows = len(df)
    except Exception as e:
        os.remove(save_path)
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {str(e)}")

    await db_manager.store_dataset_metadata(
        dataset_id=dataset_id,
        filename=file.filename,
        filepath=save_path,
        columns=columns,
    )

    return DatasetUploadResponse(
        dataset_id=dataset_id,
        filename=file.filename,
        columns=columns,
        total_rows=total_rows,
    )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_interaction(payload: ChatRequest):
    dataset_filepath = None
    if payload.dataset_id:
        meta = await db_manager.get_dataset_metadata(payload.dataset_id)
        if not meta:
            raise HTTPException(status_code=404, detail="Dataset ID not found")
        dataset_filepath = meta["filepath"]

    history = await db_manager.get_history(payload.session_id, limit=10)

    try:
        agent_output = await agent_service.run(
            session_id=payload.session_id,
            user_input=payload.message,
            history_records=history,
            dataset_filepath=dataset_filepath,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

    await db_manager.append_message(
        session_id=payload.session_id, role="user", content=payload.message
    )
    await db_manager.append_message(
        session_id=payload.session_id, role="assistant", content=agent_output["output"]
    )

    return ChatResponse(
        session_id=payload.session_id,
        response=agent_output["output"],
        intermediate_steps=agent_output["steps"],
    )


@app.get("/api/v1/history/{session_id}", response_model=list[HistoryItem])
async def get_session_history(session_id: str):
    raw_history = await db_manager.get_history(session_id, limit=30)
    return [
        HistoryItem(
            role=doc["role"],
            content=doc["content"],
            created_at=doc["created_at"],
        )
        for doc in raw_history
    ]


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AIForge"}