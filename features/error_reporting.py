"""Error reporting functionality for the quiz application."""
import smtplib
import ssl
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Optional, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.ERROR,
    filename='quiz_errors.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorReporter:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls
        self.sender_email = "remixonwin@gmail.com"
        self.password = os.getenv('QUIZ_APP_EMAIL_PASSWORD', 'reidtcyujehfgxqi')
        self.receiver_email = "remixonwin@gmail.com"

    def format_error_report(self, question_data: Dict[str, Any], error_report: str, contact_email: Optional[str]) -> str:
        """Format the error report into a readable email message."""
        report = f"""
Error Report for Minnesota Driver's Quiz Question

Question Information:
-------------------
Question: {question_data.get('question', 'N/A')}
Correct Answer: {question_data.get('correct_answer', 'N/A')}
Options: {', '.join(question_data.get('options', []))}
Topic: {question_data.get('topic', 'N/A')}

Error Report:
-----------
{error_report}

Reporter Contact:
---------------
Email: {contact_email if contact_email else 'Not provided'}
"""
        return report

    def send_error_report(self, question_data: Dict[str, Any], error_report: str, contact_email: Optional[str] = None) -> Tuple[bool, str]:
        """Send error report via email."""
        try:
            message = MIMEMultipart()
            message["Subject"] = "Quiz Question Error Report"
            message["From"] = self.sender_email
            message["To"] = self.receiver_email

            # Create the email body
            body = self.format_error_report(question_data, error_report, contact_email)
            message.attach(MIMEText(body, "plain"))

            # Create a secure SSL/TLS context
            context = ssl.create_default_context()

            # Try to log in to server and send email
            try:
                server = smtplib.SMTP(self.smtp_server, self.port)
                server.ehlo()  # Can be omitted
                server.starttls(context=context)  # Secure the connection
                server.ehlo()  # Can be omitted
                server.login(self.sender_email, self.password)
                
                # Send email
                server.sendmail(self.sender_email, self.receiver_email, message.as_string())
                logger.info("Error report email sent successfully")
                return True, "Error report submitted successfully!"
                
            except Exception as e:
                logger.error(f"Failed to send error report email: {str(e)}")
                return False, f"Failed to send error report: {str(e)}"
                
            finally:
                server.quit()

        except Exception as e:
            logger.error(f"Error preparing email: {str(e)}")
            return False, f"Error preparing email: {str(e)}"

# Create global error reporter instance
error_reporter = ErrorReporter()
