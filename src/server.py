import sys
from json import dumps
import json
from flask import Flask, request
from flask_cors import CORS

from src.error import InputError
from src import config

from src.other import clear_v1
from src.auth import auth_register_v1
from src.dm import dm_create_v1, dm_details_v1, dm_invite_v1, dm_messages_v1
from src.message import message_senddm_v1

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

# Initialize
@APP.route("/clear/v1", methods=['DELETE'])
def clear_v1_flask():
    clear_v1()
    return {}

@APP.route('/auth/register/v2', methods=['POST'])
def auth_register_v2_flask(): 
    data = request.get_json()
    a_u_id = auth_register_v1(data['email'], data['password'], data['name_first'], data['name_last'])

    return json.dumps(a_u_id)

@APP.route('/dm/create/v1', methods=['POST'])
def dm_create_v1_flask(): 
    data = request.get_json()
    dm_id = dm_create_v1(data["token"], data["u_ids"])

    return json.dumps(dm_id)

@APP.route('/dm/details/v1', methods=['GET'])
def dm_details_v1_flask(): 
    token = request.args.get("token")
    dm_id = int(request.args.get("dm_id"))
    dm_details = dm_details_v1(token, dm_id)

    return json.dumps(dm_details)

@APP.route('/dm/invite/v1', methods=['POST'])
def dm_invite_v1_flask(): 
    data = request.get_json()
    dm_invite_v1(data["token"], data["dm_id"], data["u_id"])

    return json.dumps({})

@APP.route('/dm/messages/v1', methods=['GET'])
def dm_messages_v1_flask(): 
    token = request.args.get("token")
    dm_id = int(request.args.get("dm_id"))
    start = int(request.args.get("start"))
    dm_messages = dm_messages_v1(token, dm_id, start)

    return json.dumps(dm_messages)

@APP.route('/message/senddm/v1', methods=['POST'])
def message_senddm_v1_flask(): 
    data = request.get_json()
    message_id = message_senddm_v1(data["token"], data["dm_id"], data["message"])

    return json.dumps(message_id)

if __name__ == "__main__":
    APP.run(port=config.port,debug=True) # Do not edit this port
