import { GoogleGenAI } from "@google/genai";

// Put your actual API key directly inside the quotes below:
// Change line 4 from "AIzaSy..." to:
const apiKey = process.env.GEMINI_API_KEY; // or process.env.GOOGLE_API_KEY

async function main() {
  const interaction = await ai.interactions.create({
    model: "gemini-3.6-flash",
    input: [
        {
            role:'user',
            {""}
        }
    ]",
  });

  // Extract the text output from the interaction
  const textOutput =
    interaction.output_text ||
    interaction.text ||
    interaction.outputs?.[0]?.text ||
    interaction.candidates?.[0]?.content?.parts?.[0]?.text;

  if (textOutput) {
    console.log(textOutput);
  } else {
    console.log(JSON.stringify(interaction, null, 2));
  }
}

await main();