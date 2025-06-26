from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import requests
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
MAILERSEND_API = os.getenv("SMTP_API_KEY")

class LeadInput(BaseModel):
    brand_name: str
    service: str
    ideal_client: str
    recipient_email: str

@app.post("/generate-message")
def generate_msg(data: LeadInput):
    prompt = f"""
    Write a short, personalized cold email from a brand called {data.brand_name}.
    They offer {data.service} to {data.ideal_client}.
    Make the email persuasive and focused on ROI.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    message = response.choices[0].message["content"]
    return {"message": message}

@app.post("/send-email")
def send_email(data: LeadInput):
    message_resp = generate_msg(data)
    message = message_resp["message"]

    payload = {
        "from": {
            "email": "you@yourdomain.com",  # Replace with your verified MailerSend email
            "name": data.brand_name
        },
        "to": [{"email": data.recipient_email}],
        "subject": f"{data.brand_name} can help you grow",
        "text": message
    }

    headers = {
        "Authorization": f"Bearer {MAILERSEND_API}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.mailersend.com/v1/email", json=payload, headers=headers)
    return {"status": response.status_code, "details": response.text}
