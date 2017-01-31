#!/usr/bin/env python



import os
import glob
import base64
import datetime
import argparse
import httplib2
import urllib.request

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()



SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'gmail-sbb-receipt-downloader'


SEARCH_QUERY="Ihre Bestellung im SBB Mobile Ticket Shop"
SEARCH_OPERATOR="newer_than:31d"
DOWNLOAD_PATH="/home/eni/adsy/spesen/sbb"


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-sbb-receipt.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials



def get_sbb_receipt_url(mres):
    datab64 = mres['payload']['body']['data']
    data = base64.b64decode(datab64).decode()
    for line in data.split("\n"):
        line = line.strip()
        if line.find("https://www")>-1 and line.find(".pdf")>-1:
            return line


def get_message(messages, mid):
    return messages.get(userId='me', id=mid).execute()


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    users = service.users()
    messages = users.messages()

    query = "%s %s" % (SEARCH_QUERY, SEARCH_OPERATOR)
    res = messages.list(userId='me', q=query).execute()

    find_num = res["resultSizeEstimate"]
    print("Found %i matching messages" % find_num)
    for message_id in res["messages"]:
        glob_str = "%s/*_%s.pdf" % (
            DOWNLOAD_PATH,
            message_id['id']
        )
        matches = glob.glob(glob_str)
        if matches:
            bname = os.path.basename(matches[0])
            print("Receipt %s allready exists on file system" % bname)
            continue

        message = get_message(messages, message_id['id'])
        msg_date = datetime.datetime.fromtimestamp(
            int(message['internalDate'])/1000
        ).strftime('%Y-%m-%d-%H%M')
        filename = "%s/%s_%s.pdf" % (
            DOWNLOAD_PATH,
            msg_date,
            message_id['id']
        )
        
        bname = os.path.basename(filename)
        print("Downloading %s" % bname)
        url = get_sbb_receipt_url(message)
        urllib.request.urlretrieve(url, filename)



if __name__ == '__main__':
    main()
