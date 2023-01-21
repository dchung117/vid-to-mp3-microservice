import os
import json
from typing import Optional

import smtplib
from email.message import EmailMessage

def notify(message: bytes) -> Optional[Exception]:
    try:
        # Load message from queue as JSON string, get MP3 file id
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]

        # Get notification service email/password
        sender_address = os.environ.get("HOST_EMAIL")
        sender_password = os.environ.get("HOST_PASSWORD")

        # Send notification email to user, mp3 file is ready for download
        receiver_address = message["username"]
        msg = EmailMessage()
        msg.set_content(f"MP3 file ID: {mp3_fid}. Download it at http://vidtoaudio.com/download?fid={mp3_fid} - must also provide your access token.")
        msg["Subject"] = "Your MP3 file is ready for download"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        # Create SMTP session to send email
        sess = smtplib.SMTP("smtp.gmail.com", port=587)
        sess.starttls() # TLS mode
        sess.login(sender_address, sender_password)
        sess.send_message(msg, from_addr=sender_address, to_addrs=receiver_address)
        sess.quit()
        print("Sent email.")
    except Exception as err:
        print(err)
        return err