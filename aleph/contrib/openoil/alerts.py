'''
Aleph email alert system

See documentation at  https://docs.google.com/document/d/1Fw-JaIj_9ds-XYlqFdHvBd8QLPTtpEImt5JWFWYA6hg/edit#heading=h.uyujmyqco778
'''

from aleph.model import Alert
from aleph.core import db, app
from aleph.search import search_documents
from aleph.search.queries import document_query
from envelopes import Envelope, GMailSMTP

import html2text
from flask import render_template
from jinja2 import Environment, FileSystemLoader

import os
from os.path import abspath, dirname
from datetime import datetime, timedelta

def check_alerts():
    for al in db.session.query(Alert):
        if al.due_to_check():
            run_alert(al)
            al.mark_as_checked()

def run_alert(al):
    query = build_query(al)
    results = search_documents(query)
    if should_mail_results(al, results):
        mail_results(al, results)

def build_query(al):
    last_checked =  al.checked_at or (datetime.now() - timedelta(days=al.checking_interval))
    es_date_format = '%FT%X.000'
    newerthan = last_checked.strftime(es_date_format)
    qry = document_query(args = {'q': al.query},  newerthan=newerthan)
    return qry

def should_mail_results(al, results):
    return int(results.result['hits']['total']) > 0

def mail_welcome_email(user):
    subject = 'Welcome to Aleph'
    templatedir = dirname(dirname(dirname(abspath(__file__)))) + '/templates/'
    env = Environment(loader=FileSystemLoader(templatedir))


    html_body = env.get_template('welcome_mail.html').render(**{
        'user': user,
        })
    text_body = html2text.html2text(html_body)
    
    msg = Envelope(
        from_addr = (u'aleph@openoil.net', u"Aleph"),
        to_addr = (user.email),
        subject = subject,
        text_body = text_body,
        html_body = html_body)
    msg.send(app.config.get('MAIL_HOST'),
             login=app.config.get('MAIL_FROM'),
             password=app.config.get('MAIL_PASSWORD'),
             tls=True)    

    
def mail_results(al, results):
    subject = 'Aleph: %s new documents matching %s' % (results.result['hits']['total'], al.label)
    templatedir = dirname(dirname(dirname(abspath(__file__)))) + '/templates/'
    env = Environment(loader=FileSystemLoader(templatedir))

    # every other search from the same user, for display in the mail
    other_searches = db.session.query(
        Alert).filter(Alert.user_id == al.user_id)
    
    html_body = env.get_template('alert.html').render(**{
        'hits': results.result['hits']['hits'],
        'user': al.user,
        'alert': al,
        'other_searches': other_searches})
    text_body = html2text.html2text(html_body)
    
    msg = Envelope(
        from_addr = (u'daniel.ohuiginn@openoil.net', u"Dan O'Huiginn"),
        to_addr = (al.user.email),
        subject = subject,
        text_body = text_body,
        html_body = html_body)
    msg.send(app.config.get('MAIL_HOST'),
             login=app.config.get('MAIL_FROM'),
             password=app.config.get('MAIL_PASSWORD'),
             tls=True)    

