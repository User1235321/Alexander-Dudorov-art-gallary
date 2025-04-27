from flask_mail import Mail, Message
import logging



class MailService:
    def __init__(self, mail):
        self.mail = mail
        self.logger = logging.getLogger('MailService')
        self.logger.setLevel(logging.INFO)

    def send_2fa_code(self, email, code):
        try:
            msg = Message(
                subject="Ваш код подтверждения для Art Gallery",
                recipients=[email],
                html=f"""
                                <h3>Ваш код подтверждения</h3>
                                <p>Используйте этот код для входа:</p>
                                <h2 style="font-family: monospace">{code}</h2>
                                <p><small>Код действителен 10 минут</small></p>
                                """
            )
            self.mail.send(msg)
            self.logger.info(f"Email sent: {email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            raise

mail_service = None


def init_mail_service(app):
    global mail_service
    mail = Mail(app)
    mail_service = MailService(mail)
