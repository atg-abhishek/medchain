from flask import Flask 
import sys, random
from twilio.rest import Client
import simplejson as json
from tinydb import TinyDB, Query
import shelve

db = TinyDB('./database/db.json')

app = Flask(__name__)

HOST = ""

if len(sys.argv)>1 and sys.argv[1] == "prod":
        HOST = '0.0.0.0'
else:
    HOST = None

twilio_info = {}
with open("./config/keys.json") as infile:
    twilio_info = json.load(infile)

ACCOUNT_SID = twilio_info['twilio_sid']
AUTH_TOKEN = twilio_info["twilio_token"]

test_info = {}
with open("./config/test_info.json") as infile:
    test_info = json.load(infile)

def send_message(message, sender=test_info['sender'], receiver=test_info['receiver']):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    client.messages.create(
        to = receiver,
        from_ = sender,
        body = message
    )

# def generate_challenge():
#     return     

def write_code(code, number):
    with shelve.open('./database/codes') as shelf:
        shelf[code] = number
    return "code written"

@app.route('/hello')
def code():
    write_code("1234", "12312")
    return "done"

@app.route('/')
def hello():
    return "hello"

if __name__ == "__main__":
    app.run(debug=True, host=HOST)