from flask import Flask, request, redirect, url_for
import sys, random, time
from twilio.rest import Client
import simplejson as json
from tinydb import TinyDB, Query
import shelve, requests

db = TinyDB('./database/db.json')

app = Flask(__name__)

HOST = ""
SHELF_ADDRESS = "./database/codes"
CODE_ATTEMPTS_LIMIT = 10
CODE_GEN_START = 100000
CODE_GEN_STOP = 999999

# following helps to avoid having to configure the server to run on public IP when remote and localhost when testing locally
if len(sys.argv)>1 and sys.argv[1] == "prod":
        HOST = '0.0.0.0'
else:
    HOST = None

twilio_info = {}
with open("./config/keys.json") as infile:
    twilio_info = json.load(infile)

ACCOUNT_SID = twilio_info['twilio_sid']
AUTH_TOKEN = twilio_info["twilio_token"]

# this will contain all the test information, like test numbers
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

def generate_challenge(number):
    code_attempts = 1
    unique = True 
    while (unique):
        if code_attempts<=CODE_ATTEMPTS_LIMIT:
            code = str(random.randint(CODE_GEN_START,CODE_GEN_STOP))
            with shelve.open(SHELF_ADDRESS) as shelf:
                if code in shelf:
                    code_attempts += 1
                    continue
                else:
                    shelf[code] = number
                    unique = False
                    return code
        else:
            code_attempts = 1
            flush_keys()
            

def flush_keys():
    with shelve.open(SHELF_ADDRESS) as shelf:
        lst = list(shelf.keys())
        lst = lst[:int(len(lst)/2)]
        for k in lst:
            del shelf[k]          

@app.route('/')
def hello():
    return "hello"

@app.route("/gen_code", methods=['POST'])
def gen_code():
    body = request.form 
    number = body['number']
    res = generate_challenge(number)
    send_message(res)
    return "check the phone for the code"

res = generate_challenge("1234")
print("result is " + res)
# if __name__ == "__main__":
#     app.run(debug=True, host=HOST, threaded=True)