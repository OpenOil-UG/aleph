import logging
from flask import render_template
from flask_mail import Message

from aleph.core import get_config, mail, get_app_url

log = logging.getLogger(__name__)


def notify_role(role, subject, html):
    if role.email is None:
        log.error("Role does not have E-Mail: %r", role)
        return

    email_name = get_config('MAIL_SENDER', get_config('APP_TITLE'))
    sender = '%s <%s>' % (email_name,
                          get_config('MAIL_FROM'))
    subject = '[%s] %s' % (get_config('APP_TITLE'), subject)
    msg = Message(subject=subject,
                  sender=sender,
                  recipients=[role.email])
    msg.html = html
    mail.send(msg)

def send_welcome_mail(role):
    subject = 'Welcome to Aleph'
    html = render_template('mail/welcome_mail.html', 
                           app_url=get_app_url())
    notify_role(role, subject, html)
