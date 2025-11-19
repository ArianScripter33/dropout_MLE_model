import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # REPLACE THIS
SENDER_PASSWORD = "your-app-password"  # REPLACE THIS
# Link to the video/image of the winner (e.g., Instagram post, YouTube video, Drive link)
WINNERS_LINK = "https://instagram.com/pulso_unrc" # REPLACE THIS
# Resolve path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "../data/processed/datos_limpios.csv")

def send_email(recipient_email, subject, html_content):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, recipient_email, text)
        server.quit()
        print(f"✅ Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send to {recipient_email}: {e}")
        return False

def main():
    # Load data
    if not os.path.exists(CSV_PATH):
        print(f"Error: File not found at {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)
    
    # Filter participants
    participants = df[df['participa_sorteo'] == 'Sí']
    
    print(f"Found {len(participants)} participants.")
    
    # Premium HTML Template
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #0F0F0F; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0F0F0F; padding: 40px 0;">
        <tr>
            <td align="center">
                <table role="presentation" width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #1A1A1A; border-radius: 16px; border: 1px solid #333333; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #FACC15; font-size: 28px; font-weight: 700;">Pulso Estudiantil UNRC</h1>
                            <p style="margin: 10px 0 0 0; color: #888888; font-size: 16px;">Tu voz cuenta</p>
                        </td>
                    </tr>
                    <tr>
                        <td align="center">
                            <div style="width: 80%; height: 1px; background: linear-gradient(90deg, transparent, #333333, transparent);"></div>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px; color: #E5E5E5; font-size: 16px; line-height: 1.6;">
                            <p style="margin-bottom: 20px;">Hola,</p>
                            <p style="margin-bottom: 20px;">Queremos agradecerte enormemente por participar en nuestra encuesta. Tu opinión es fundamental para construir un mejor sistema de apoyo estudiantil.</p>
                            <p style="margin-bottom: 30px;">Como prometimos, has sido incluido en el sorteo de premios exclusivos.</p>
                            <table role="presentation" border="0" cellspacing="0" cellpadding="0" width="100%">
                                <tr>
                                    <td align="center">
                                        <a href="{WINNERS_LINK}" style="display: inline-block; background: linear-gradient(135deg, #FACC15 0%, #CA8A04 100%); color: #000000; font-weight: bold; text-decoration: none; padding: 16px 32px; border-radius: 50px; font-size: 16px;">
                                            Ver Ganadores del Sorteo
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #111111; padding: 30px; text-align: center; border-top: 1px solid #2A2A2A;">
                            <p style="margin: 0; color: #666666; font-size: 12px;">© 2025 Pulso Estudiantil UNRC.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """

    # Safety Confirmation
    print("\n" + "="*50)
    print("⚠️  SAFETY CHECK ⚠️")
    print(f"You are about to send emails to {len(participants)} participants.")
    print("This action cannot be undone.")
    print("To confirm, please type the following phrase exactly:")
    print("CONFIRM_SEND_ALL")
    print("="*50 + "\n")
    
    confirm = input("Confirmation: ")
    if confirm != 'CONFIRM_SEND_ALL':
        print("❌ Confirmation failed. Aborting.")
        return

    print("\n🚀 Starting email blast...")

    # Send loop
    for index, row in participants.iterrows():
        email = row['email']
        if pd.isna(email) or '@' not in str(email):
            print(f"Skipping invalid email: {email}")
            continue
            
        # Inject the link into the template
        email_content = html_template.format(WINNERS_LINK=WINNERS_LINK)
        send_email(email, "Sorteo Pulso Estudiantil - ¡Gracias!", email_content)
        time.sleep(1) # Avoid rate limits

if __name__ == "__main__":
    main()
