import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import base64
import os
from datetime import datetime

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            if filename.endswith('.txt'):
                f.write('[]' if 'subscribers' in filename else '{}')
    with open(filename, 'r') as f:
        return json.load(f)

def get_pending_tasks():
    tasks = load_json('tasks.txt')
    return [task for task in tasks if not task['completed']]

def get_subscribers():
    return load_json('subscribers.txt')

def send_reminder(email, pending_tasks):
    sender = "vishwajakakulate@gmail.com"  # Use a testing account
    password = "fbuo ngel khyt hnka"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📝 Task Reminder"
    msg["From"] = sender
    msg["To"] = email

    task_list = "".join(f"<li>{task['name']}</li>" for task in pending_tasks)
    encoded_email = base64.urlsafe_b64encode(email.encode()).decode()
    unsubscribe_link = f"http://localhost:5000/unsubscribe?email={encoded_email}"

    html = f"""
    <html>
    <body>
        <p>Hi! 👋<br>
        Here are your pending tasks:</p>
        <ul>{task_list}</ul>
        <p><a href="{unsubscribe_link}">Unsubscribe</a></p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, email, msg.as_string())
            print(f"✅ Sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send to {email}: {e}")

def send_reminders():
    subscribers = get_subscribers()
    tasks = get_pending_tasks()

    if not tasks:
        print("🎉 No pending tasks!")
        return

    for email in subscribers:
        send_reminder(email, tasks)

if __name__ == "__main__":
    send_reminders()
