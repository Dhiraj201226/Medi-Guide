from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MediGuide AI API")

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.getenv("HF_TOKEN")
# Using Mistral as recommended via the new HF Router API
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def chat(req: ChatRequest):
    prompt = f"""You are MediGuide AI, a professional medical and health assistant. Analyze the user's symptoms and provide structured guidance.
Be thorough and consider severe implications (e.g. internal bleeding for nose bleeds + vomiting). Do NOT provide a full medical diagnosis, just guidance.
If symptoms are potentially life-threatening or serious, automatically elevate the Risk Level to High.

Return EXACTLY in this format (do not add extra text outside this format):
Possible Causes:
- [cause 1]
- [cause 2]

Risk Level:
[Low/Medium/High]

Reason for Risk Level:
[Explain why this risk level was chosen and what follow-up questions might be relevant]

Recommended Action:
[action]

Health Tips:
- [tip 1]
- [tip 2]

Medical Disclaimer:
[Provide a strong medical disclaimer here]

Symptoms:
{req.message}"""

    try:
        from g4f.client import Client
        client = Client()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        
        generated_text = response.choices[0].message.content
        return {"response": generated_text.strip()}
            
    except Exception as e:
        print(f"g4f API Error: {e}")
        fallback_msg = f"""Possible Causes:
- Simulated response (AI connection failed)
- Network issue reaching the AI provider

Risk Level:
Medium

Recommended Action:
Please check your internet connection or try again later. 

Health Tips:
- This is a fallback message because the AI server could not be reached.
- Error details: {str(e)[:100]}..."""
        return {"response": fallback_msg}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
