from fastapi import FastAPI
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_MAIL="foundersnexusfastapi@gmail.com"
SMTP_PASSWORD="pomr jvfu ubeu kqgu"

def send_mail(to, subject, body, attachment=None):
    msg = MIMEMultipart()
    msg['From'] = SMTP_MAIL
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_MAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_MAIL, to, msg.as_string())
    server.quit()

    return {"message": "Email sent successfully"}


send_mail("kelam@yopmail.com","test","this is test mail ")