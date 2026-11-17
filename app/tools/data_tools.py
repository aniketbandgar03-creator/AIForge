import os
import json
from typing import Any, Dict
import pandas as pd
import numpy as np
from langchain_core.tools import tool


class DataPipelineEngine:
    @staticmethod
    def load_df(filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File at {filepath} does not exist.")
        return pd.read_csv(filepath)

    @staticmethod
    def compute_summary(df: pd.DataFrame) -> Dict[str, Any]:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        summary = {
            "total_rows": int(len(df)),
            "columns": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_metrics": {},
        }
        for col in numeric_cols:
            clean_series = df[col].dropna().to_numpy()
            if clean_series.size > 0:
                summary["numeric_metrics"][col] = {
                    "mean": float(np.mean(clean_series)),
                    "std_dev": float(np.std(clean_series)),
                    "median": float(np.median(clean_series)),
                    "min": float(np.min(clean_series)),
                    "max": float(np.max(clean_series)),
                    "variance": float(np.var(clean_series)),
                }
        return summary

    @staticmethod
    def detect_outliers(df: pd.DataFrame, column: str, threshold: float = 2.0) -> Dict[str, Any]:
        if column not in df.columns:
            return {"error": f"Column '{column}' not found"}
        vals = df[column].dropna().to_numpy()
        mean = np.mean(vals)
        std = np.std(vals)
        if std == 0:
            return {"outliers_detected": 0, "indices": []}
        z_scores = (vals - mean) / std
        outlier_mask = np.abs(z_scores) > threshold
        return {
            "column": column,
            "threshold_z_score": threshold,
            "outliers_detected": int(np.sum(outlier_mask)),
            "outlier_values": vals[outlier_mask].tolist()[:10],
        }


@tool
def analyze_dataset_statistics(filepath: str) -> str:
    """Computes summary metrics (mean, std, median, nulls) for numeric columns in a CSV."""
    try:
        df = DataPipelineEngine.load_df(filepath)
        stats = DataPipelineEngine.compute_summary(df)
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def run_dataset_outlier_detection(filepath: str, column: str, threshold: float = 2.0) -> str:
    """Identifies outliers in a given numerical column using NumPy Z-scores."""
    try:
        df = DataPipelineEngine.load_df(filepath)
        result = DataPipelineEngine.detect_outliers(df, column, threshold)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def execute_dataframe_query(filepath: str, query_expr: str) -> str:
    """Executes a Pandas boolean query expression (e.g. 'sales > 1000') on the dataset."""
    try:
        df = DataPipelineEngine.load_df(filepath)
        filtered_df = df.query(query_expr)
        result = {
            "matched_records": len(filtered_df),
            "percentage_of_total": round((len(filtered_df) / len(df)) * 100, 2),
            "sample_records": filtered_df.head(5).to_dict(orient="records"),
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to execute query: {str(e)}"})