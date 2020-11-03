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
import json

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def send_message(sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('gmail', 'v1', http=http)
    message = html_message(sender, to, subject, msgHtml, msgPlain)
    result = send_message_internal(service, "me", message)
    return result


def send_message_internal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except apiclient.errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"


def html_message(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode()}


def read_url_list():
    with open('url_list.txt', 'r') as f:
        url_txt = f.read()
    url_list = url_txt.split()
    return url_list


def initialize_inventory(url_list):
    if os.path.exists('inventory.json'):
        return
    url_list = read_url_list()
    inventory = {url: [] for url in url_list}
    dump_inventory(inventory)


def dump_inventory(inventory):
    inventory = {key: list(set(item)) for key, item in inventory.items()}
    with open('inventory.json', 'w') as f:
        json.dump(inventory, f, indent=4)


def read_inventory():
    with open('inventory.json', 'r') as f:
        inventory = json.load(f)
    inventory = {key: set(item) for key, item in inventory.items()}
    return inventory


def get_new_items(url_list):
    items = {}
    for url in url_list:
        items[url] = get_item_info(url)
    return items


def update_inventory(inventory, new_items):
    email_list = []
    for url, items in new_items.items():
        item_ids = set(items.keys())
        ids_to_send = [i for i in item_ids if i not in inventory[url]]
        for item_id in ids_to_send:
            email_list.append(items[item_id])
        inventory[url] = item_ids
    return inventory, email_list


def get_item_info(url):
    base_url = 'https://wornwear.patagonia.com'
    search_url = f'{base_url}/{url}'
    code = requests.get(search_url)
    s = BeautifulSoup(code.text, 'html.parser')
    items = s.find_all('li', class_='TileItem')
    item_dict = {}
    for item in items:
        img_url = item.find('img')['src']
        item_id = img_url.split('inventoryItem/')[1].split('/')[0]
        item_dict[item_id] = {}
        item_dict[item_id]['label'] = item['aria-label']
        item_url = item.find('a', href=True)['href']
        item_dict[item_id]['item_url'] = f'{base_url}{item_url}'
    return item_dict


def make_email(email_list):
    # compose the email content here
    to = "tyler.a.martin12@gmail.com"
    sender = "tyler.a.martin12@gmail.com"
    subject = "worn wear"
    msgHtml = 'WW summary: <br/> <br/>'
    for item in email_list:
        msgHtml += f"{item['label']} at {item['item_url']} <br/> <br/>"
    msgPlain = ''
    send_message(sender, to, subject, msgHtml, msgPlain)
    return msgHtml


def start_watching():
    url_list = read_url_list()
    initialize_inventory(url_list)
    inventory = read_inventory()
    new_items = get_new_items(url_list)
    inventory, email_list = update_inventory(inventory, new_items)
    if len(email_list) > 0:
        msg = make_email(email_list)
    dump_inventory(inventory)
    print(f'{len(email_list)} items added')


if __name__ == '__main__':
    start_watching()
