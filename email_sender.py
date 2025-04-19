import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Dict, Optional
import logging
from datetime import datetime
from rate_limiter import RateLimiter
from metrics_tracker import MetricsTracker

class EmailSender:
    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config
        self.rate_limiter = RateLimiter()
        self.metrics = MetricsTracker()
        
        # Configure logging
        logging.basicConfig(
            filename=f'email_logs_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def send_email(
        self,
        to_addr: str,
        subject: str,
        html_content: str,
        plain_content: str,
        attachments: Optional[List[str]] = None,
        custom_headers: Optional[Dict] = None
    ) -> Dict:
        """Send an email with full tracking and security features."""
        try:
            # Check rate limits
            self.rate_limiter.check_limit()
            
            # Create message
            msg = MIMEMultipart('mixed')
            alt = MIMEMultipart('alternative')
            
            # Essential headers for better deliverability
            msg['Subject'] = subject
            msg['From'] = f"{self.smtp_config.get('sender_name', 'Kevin Garcia')} <{self.smtp_config['sender']}>"
            msg['To'] = to_addr
            msg['Message-ID'] = f"<{datetime.now().strftime('%Y%m%d%H%M%S')}.{abs(hash(to_addr))}@{self.smtp_config['domain']}>"
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
            msg['Return-Path'] = self.smtp_config['sender']
            
            # RFC compliance headers
            msg['MIME-Version'] = '1.0'
            msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
            msg['List-Unsubscribe'] = f'<https://{self.smtp_config["domain"]}/unsubscribe>, <mailto:unsubscribe@{self.smtp_config["domain"]}?subject=unsubscribe>'
            
            # Deliverability headers
            msg['Feedback-ID'] = f'Test:kevin.garcia:{datetime.now().strftime("%Y%m%d")}:{abs(hash(to_addr))}'
            msg['X-Entity-Ref-ID'] = f'Test-{datetime.now().strftime("%Y%m%d%H%M%S")}'
            
            # Remove potentially problematic headers
            headers_to_remove = ['Authentication-Results', 'Received-SPF']
            
            # Add custom headers
            if custom_headers:
                for key, value in custom_headers.items():
                    if key not in headers_to_remove:
                        msg[key] = value
            
            # Improve HTML content
            improved_html = f"""
            <!DOCTYPE html>
            <html lang="nl">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta name="color-scheme" content="light">
                <meta name="supported-color-schemes" content="light">
            </head>
            <body style="margin: 0; padding: 0; background-color: #f5f5f5;">
                {html_content}
            </body>
            </html>
            """
            
            # Add content parts
            text_part = MIMEText(plain_content, 'plain', 'utf-8')
            html_part = MIMEText(improved_html, 'html', 'utf-8')
            
            alt.attach(text_part)
            alt.attach(html_part)
            msg.attach(alt)
            
            # Handle attachments
            if attachments:
                for attachment_path in attachments:
                    with open(attachment_path, 'rb') as f:
                        part = MIMEApplication(f.read())
                        part.add_header(
                            'Content-Disposition',
                            'attachment',
                            filename=attachment_path.split('/')[-1]
                        )
                        msg.attach(part)
            
            # Connect to SMTP server
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls(context=context)
                try:
                    server.login(
                        self.smtp_config['username'],
                        self.smtp_config['password']
                    )
                except smtplib.SMTPAuthenticationError as e:
                    logging.error(f"Authentication failed for {self.smtp_config['username']}: {str(e)}")
                    raise
                
                # Send email
                result = server.send_message(msg)
                
                # Track metrics
                self.metrics.track_delivery(to_addr)
                
                logging.info(f"Email sent successfully to {to_addr}")
                return {
                    'status': 'success',
                    'recipient': to_addr,
                    'message_id': msg['Message-ID'],
                    'smtp_server': self.smtp_config['host']
                }
                
        except Exception as e:
            logging.error(f"Failed to send email to {to_addr}: {str(e)}")
            self.metrics.track_failure(to_addr, str(e))
            return {
                'status': 'error',
                'recipient': to_addr,
                'error': str(e)
            }