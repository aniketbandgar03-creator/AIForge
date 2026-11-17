import { GoogleGenAI } from "@google/genai";

// If the GEMINI_API_KEY environment variable is set, passing it explicitly is optional.
const ai = new GoogleGenAI({ apiKey: "YOUR_API_KEY" });

async function main() {
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: "Explain how AI works in a few words",
  });

  console.log(response.text);
}

await main();