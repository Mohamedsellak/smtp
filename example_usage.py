from email_sender import EmailSender
import os
import json

def read_template(filename):
    template_path = os.path.join('templates', filename)
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_smtp_config(filename='smtp_config.json'):
    """Read SMTP config from JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Return default config if file not found
        return {
            'sender': 'admin@sellak.com',
            'username': 'admin@sellak.com',
            'password': 'Mohamedsellak',
            'domain': 'sellak.online',
            'host': 'sellak.online',
            'port': 25,
            'sender_name': 'Sellak'
        }

# Read SMTP configuration from file
smtp_config = read_smtp_config()

# Create email sender instance
sender = EmailSender(smtp_config)

# Update SMTP configuration
smtp_config['sender_name'] = 'Welcome Team'

# Read templates
html_template = read_template('template.html')
text_template = read_template('template.txt')

# Prepare template variables
template_vars = {
    'tracking_link': 'https://sellak.online',
    'domain': smtp_config['domain'],
    'unsubscribe_link': f'mailto:unsubscribe@{smtp_config["domain"]}?subject=unsubscribe'
}

# Format templates with variables
html_content = html_template.format(**template_vars)
plain_content = text_template.format(**template_vars)

# Send email with improved content
result = sender.send_email(
    # to_addr='monicafue@hotmail.com',
    to_addr='hammadiotmane4@gmail.com',
    subject='Welcome to our community!',
    html_content=html_content,
    plain_content=plain_content,
    custom_headers={
        'X-Priority': '3',
        'Importance': 'Normal',
        'X-Campaign-Type': 'welcome',
        'List-Unsubscribe': f'<mailto:unsubscribe@{smtp_config["domain"]}?subject=unsubscribe>',
        'X-Report-Abuse': f'Please report abuse here: abuse@{smtp_config["domain"]}',
        'X-Mailer': 'Welcome Mailer 1.0'
    }
)

print(result)