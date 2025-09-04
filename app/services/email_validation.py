import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAIL_FROM = os.getenv("MAIL_FROM")
BASE_URL = os.getenv("BASE_URL")

def send_verification_email(to_email: str, token: str):
    verification_link = f"{BASE_URL}/auth/verify-email/{token}"  # 👈 armamos link dinámico

    subject = "Verifica tu cuenta en Mi Contaplus"
    plain_body = f"""
    ¡Bienvenido a Mi Contaplus!  
    Por favor haz clic en el siguiente enlace para verificar tu correo:  
    {verification_link}

    Este enlace expira en 24 horas.
    """
    html_body = f"""
    <h3>¡Bienvenido a <strong>Mi Contaplus</strong> 🚀</h3>
    <p>Por favor haz clic en el siguiente enlace para verificar tu correo:</p>
    <a href="{verification_link}">{verification_link}</a>
    <p><small>Este enlace expira en 24 horas.</small></p>
    """

    message = Mail(
        from_email=MAIL_FROM,
        to_emails=to_email,
        subject=subject,
        plain_text_content=plain_body,
        html_content=html_body,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[SendGrid] Email enviado a {to_email}, status {response.status_code}")
        return True
    except Exception as e:
        print(f"[SendGrid] Error: {e}")
        return False
