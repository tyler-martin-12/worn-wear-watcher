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
#import apiclient
#from apiclient import errors, discovery
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
    code = requests.get(url)
    s = BeautifulSoup(code.text, 'html.parser')
    source = s.find_all('span', class_='title')

    num = 0

    falsifiers = ['Sorry','Shop']

    for item in source:
        item_title = item.text

        nope = 0
        for f in falsifiers:
            if f in item_title:
                nope = 1

        if nope == 0:
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
    #msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode()}

def is_available(url,keywords):
    b = 1
    code = requests.get(url)
    s = BeautifulSoup(code.text, 'html.parser')
    r = s.find_all('span', class_='title')
    for each in r:
        txt = each.text
        if txt.find('Sorry') > -1:
            b = 0
        for keyword in keywords:
            if txt.find(keyword) > -1:
                #print(txt)
                b = 0
    if b == 0:
        return False
    else:
        return True


def main(url, flag):
    to = "tyler.a.martin12@gmail.com"
    sender = "tyler.a.martin12@gmail.com"
    subject = "worn wear"
    msgHtml = 'This item is available' + '<br/>' + url
    msgPlain = ''
    SendMessage(sender, to, subject, msgHtml, msgPlain, flag)

class worker(object):
    def __init__(self):
        self.urls = []
        url_list = []

        # Any 32
        url_list.append('https://wornwear.patagonia.com/shop/search?size=32&category=Pants&q=performance%20jeans')

        # Any 33
        url_list.append('https://wornwear.patagonia.com/shop/search?size=33&category=Pants&q=performance%20jeans')
        
        # Any 34
        url_list.append('https://wornwear.patagonia.com/shop/search?size=34&category=Pants&q=performance%20jeans')
        
        for i in range(len(url_list)):
            self.urls.append((url_list[i],0))
            
    def job(self):
        parser = argparse.ArgumentParser(parents=[tools.argparser])
        flag = parser.parse_args()
        #print(flag)

        next_num = []

        for url, prev_num in self.urls:
            num = num_items(url)
            
            if num > prev_num:
                main(url, flag)
                
            next_num.append(num)

        for i in range(len(self.urls)):
            self.urls[i] = self.urls[i][0], next_num[i]

        run_time = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
        print('script ran at ' + run_time)
        print(next_num)


my_worker = worker()
scheduler = BlockingScheduler()
scheduler.add_job(my_worker.job, 'interval', minutes=20)
scheduler.start()