import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from .email_formatter import format_email_content
load_dotenv()

def send_email_gmail(sender_email, sender_password, receiver_email, content):
    try:
        # Set up the SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Create the email content
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = os.getenv("EMAIL_SUBJECT")
        content = format_email_content(content)
        msg.attach(MIMEText(content, "html"))

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


        