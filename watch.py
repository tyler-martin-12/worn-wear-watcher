"""
gmail api code adapted from stackover user 'apadana' from below
https://stackoverflow.com/questions/37201250/sending-email-via-gmail-python/37267330
"""

from apscheduler.schedulers.blocking import BlockingScheduler
import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import requests
from bs4 import BeautifulSoup
import datetime
import argparse

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'

def get_credentials(flag):
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store,flags)
        print('Storing credentials to ' + credential_path)
    return credentials

def num_items(url):
    # returns the number of items available from the url
    code = requests.get(url)
    s = BeautifulSoup(code.text, 'html.parser')
    source = s.find_all('span', class_='title')

    num = 0

    # these appear when 0 items are available and must be checked
    falsifiers = ['Sorry','Shop']

    for item in source:
        item_title = item.text

        item_is_real = True
        for f in falsifiers:
            if f in item_title:
                item_is_real = False

        if item_is_real == True:
            num += 1
        
    return num

def SendMessage(sender, to, subject, msgHtml, msgPlain, flag, attachmentFile=None):
    credentials = get_credentials(flag)
    http = credentials.authorize(httplib2.Http())
    #service = apiclient.discovery.build('gmail', 'v1', http=http)
    service = build('gmail', 'v1', http=http)
    if attachmentFile:
        message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    else: 
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except apiclient.errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"

def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode()}

def make_email(url, flag):
    # compose the email content here
    to = "tyler.a.martin12@gmail.com"
    sender = "tyler.a.martin12@gmail.com"
    subject = "worn wear"
    msgHtml = 'This item is available' + '<br/>' + url
    msgPlain = ''
    SendMessage(sender, to, subject, msgHtml, msgPlain, flag)

class watcher(object):
    def __init__(self):
        self.urls = []
        url_list = []

        # Size 32 Men's Performance Jeans
        url_list.append('https://wornwear.patagonia.com/shop/search?size=32&category=Pants&q=performance%20jeans')

        # Size 33 Men's Performance Jeans
        url_list.append('https://wornwear.patagonia.com/shop/search?size=33&category=Pants&q=performance%20jeans')
        
        # Size 34 Men's Performance Jeans
        url_list.append('https://wornwear.patagonia.com/shop/search?size=34&category=Pants&q=performance%20jeans')
        
        for i in range(len(url_list)):
            self.urls.append((url_list[i],0))
            
    def job(self):
        parser = argparse.ArgumentParser(parents=[tools.argparser])
        flag = parser.parse_args()

        next_num = []

        for url, prev_num in self.urls:
            num = num_items(url)
            
            if num > prev_num:
                make_email(url, flag)
                
            next_num.append(num)

        for i in range(len(self.urls)):
            self.urls[i] = self.urls[i][0], next_num[i]

        run_time = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
        print('script ran at ' + run_time)
        print(next_num)


my_watcher = watcher()
scheduler = BlockingScheduler()
# change the execution iterval below
scheduler.add_job(my_watcher.job, 'interval', minutes=1)
scheduler.start()