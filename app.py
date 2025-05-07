from flask import Flask, request, jsonify
import openai
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
import base64

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("gmail", "v1", credentials=creds)

def send_email(service, to, subject, body):
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["From"] = "me"
    message["Subject"] = subject
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
    return result

@app.route('/send-email', methods=['POST'])
def handle_send_email():
    data = request.get_json()
    name = data['name']
    email = data['email']
    topic = data['topic']

    prompt = f"Write a warm, helpful email to {name} about {topic}, from a financial advisor at Financial Lend."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    ai_message = response['choices'][0]['message']['content']

    service = get_gmail_service()
    sent = send_email(service, email, f"Information on {topic}", ai_message)

    return jsonify({"status": "success", "message_id": sent['id']}), 200

if __name__ == '__main__':
    app.run(debug=True)
