from fastapi import FastAPI
from pydantic import BaseModel
import openai, requests, os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")
SMTP_API_KEY = os.getenv("SMTP_API_KEY")

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
    Make the email persuasive and focused on ROI. Add this Calendly link: https://calendly.com/YOUR-LINK
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"message": response.choices[0].message["content"]}

@app.post("/send-email")
def send_email(data: LeadInput):
    message = generate_msg(data)["message"]
    email_data = {
        "from": {"email": "you@yourdomain.com", "name": data.brand_name},
        "to": [{"email": data.recipient_email}],
        "subject": f"{data.brand_name} can help you grow",
        "text": message
    }
    headers = {
        "Authorization": f"Bearer {SMTP_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post("https://api.mailersend.com/v1/email", json=email_data, headers=headers)
    return {"status": response.status_code, "details": response.text}
