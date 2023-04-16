from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

app = Flask('')

mail = Mail()

MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_SERVER = os.getenv('MAIL_SERVER')




app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

def emailsend(username, email, code):
    print("emailsend function called")

    try:
        with app.app_context():
            msg = Message(f'Hello {username}!', sender = 'Rusty Memories', recipients = [f'{email}'])
            msg.subject = "Your verification code"
            msg.html = f"""
            <div style="text-align: center;">
                <h1 style="font-weight: 500;">Great to see you,</h1> 
                <div style="font-size: 40px; font-weight: 600;">{username}!</div>
                <div style="font-size: 50px;">🥵</div>
                <h2 style="font-weight: 500;">Here is your verification code:<h2>
                <div style="font-size: 50px; font-weight: 600;">{code}</div>
                <h2 style="font-weight: 500;">Have a fantastic day, and remember to stay Rusty!<h2>

            
                <br>
                <div style="font-weight: 500;">Rusty Memories</div>
                <div>
        </div>
            """
            mail.send(msg)
            print("sent")
    except:
        print("error")
        pass
