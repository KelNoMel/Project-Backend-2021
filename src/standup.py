# PROJECT-BACKEND: Team Echo
# Written by Darrell Mounarath

from src.data import retrieve_data
from src.error import AccessError, InputError
from src.auth import auth_token_ok, auth_decode_token
from src.message import message_send_v2
import threading
import time
from datetime import datetime

# THREAD FUNCTION
def send_message(token, channel_id, length, time_finish):
    data = retrieve_data()

    data['channels'][channel_id]['standup']['is_active'] = True
    data['channels'][channel_id]['standup']['time_finish'] = time_finish
    time.sleep(length)
    message_str = ""
    for message in messages:
        message_str += f"{message}" if message == messages[-1] else f"{message}\n"
    message_send_v2(token, channel_id, message_str)
    data['channels'][channel_id]['standup']['is_active'] = False
    data['channels'][channel_id]['standup']['time_finish'] = None

# ASSUMPTION: Length cannot be negative, and can be as large as any amount
def standup_start_v1(token, channel_id, length):
    '''
    BRIEF DESCRIPTION
    For a given channel, start the standup period whereby for the next "length" seconds 
    if someone calls "standup_send" with a message, it is buffered during the X second window 
    then at the end of the X second window a message will be added to the message queue 
    in the channel from the user who started the standup. 
    X is an integer that denotes the number of seconds that the standup occurs for

    Arguments:
        token (string)   - Token belonging to caller
        channel_id (int) - ID belonging to given channel
        length (int)     - Number of secconds the standup occurs for

    Exceptions:
        InputError  - Channel ID is not a valid channel
        InputError  - An active standup is currently running in this channel
        AccessError - Authorised user is not in the channel
        AccessError - Invalid token

    Returns:
        Returns time_finish
    '''

    data = retrieve_data()

    # Checks if channel_id is valid
    if channel_id not in data['channels']: raise InputError

    # Checks if token exists
    if not auth_token_ok(token): raise AccessError
    auth_user_id = auth_decode_token(token)

    # Checks if user belongs in channel
    if auth_user_id not in data['channels'][channel_id]['all_members']: raise AccessError

    # Checks if standup exists
    if data['channels'][channel_id]['standup']['is_active'] == True: raise InputError

    global messages
    messages = []
    
    time_finish = int(datetime.now().timestamp() + length)
    t = threading.Thread(target=send_message, args=(token, channel_id, length, time_finish))
    t.start()

    return {"time_finish" : time_finish}

# ASSUMPTION: standup_active can be called by anyone, no matter whether they are in the channel or not
def standup_active_v1(token, channel_id):
    '''
    BRIEF DESCRIPTION
    For a given channel, return whether a standup is active in it, and what time the standup finishes. 
    If no standup is active, then time_finish returns None.

    Arguments:
        token (string)   - Token belonging to caller
        channel_id (int) - ID belonging to given channel

    Exceptions:
        InputError  - Channel ID is not a valid channel
        AccessError - Invalid token

    Returns:
        Returns a dict that contains time_finish and is_active
    '''

    data = retrieve_data()

    # Checks if channel_id is valid
    if channel_id not in data['channels']: raise InputError

    # Checks if token exists
    if not auth_token_ok(token): raise AccessError

    return {"is_active" : data['channels'][channel_id]['standup']['is_active'], "time_finish" : data['channels'][channel_id]['standup']['time_finish']}

def standup_send_v1(token, channel_id, message):
    '''
    BRIEF DESCRIPTION
    Sending a message to get buffered in the standup queue, 
    assuming a standup is currently active.

    Arguments:
        token (string)   - Token belonging to caller
        channel_id (int) - ID belonging to given channel
        message (string) - Message content

    Exceptions:
        InputError  - Channel ID is not a valid channel
        InputError  - Message is more than 1000 characters (not including the username and colon)
        InputError  - An active standup is not currently running in this channel
        AccessError - The authorised user is not a member of the channel that the message is within
        AccessError - Invalid token

    Returns:
        Returns nothing
    '''

    data = retrieve_data()

    # Checks if channel_id is valid
    if channel_id not in data['channels']: raise InputError

    # Checks if token exists
    if not auth_token_ok(token): raise AccessError
    auth_user_id = auth_decode_token(token)

    # Checks if user belongs in channel
    if auth_user_id not in data['channels'][channel_id]['all_members']: raise AccessError

    # Checks if standup exists
    if data['channels'][channel_id]['standup']['is_active'] == False: raise InputError

    # Check to see if the message is too long
    if len(message) > 1000: raise InputError

    new_message = f"{data['users'][auth_user_id]['handle_str']}: {message}"

    global messages
    messages.append(new_message)