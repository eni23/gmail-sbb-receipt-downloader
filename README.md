# gmail-sbb-receipt-downloader

This quick and dirty python script downloads all SBB receipts from your gmail account.


## Howto setup auth

Enable API and setup a new app following this wizard:
https://console.developers.google.com/start/api?id=gmail
Click Continue, then Go to credentials.
You need to create credentials that access user data.
Download the json file to `client_secret.json` inside the same directory as the python script.

## Running

```
virtualenv venv-gmail
source venv-gmail/bin/activate
pip install --upgrade google-api-python-client

./get_receipt.py
```

## Configuration

Config is currently done directly inside `get_receipt.py`
