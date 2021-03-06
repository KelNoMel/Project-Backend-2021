# PROJECT-BACKEND: Team Echo
# Written by Brendan Ye

from src.data import retrieve_data
from src.error import AccessError, InputError
from src.auth import auth_token_ok, auth_decode_token
from uuid import uuid4
from datetime import datetime
import json
import re

import threading # Used for timer

###############################################################################
#                                  FUNCTIONS                                  #
###############################################################################

def message_send_v2(token, channel_id, message):
    '''
    BRIEF DESCRIPTION
    Send a message from authorised_user to the channel specified by channel_id. 
    Note: Each message should have it's own unique ID. I.E. No messages should 
    share an ID with another message, even if that other message is in a 
    different channel.

    Arguments:
        token (string)          - User that sends the messages
        channel_id (int)        - Channel to send message
        message (string)        - Message content

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the authorised user has not joined the channel they are trying to post to
        InputError  - Occurs when the message is more than 1000 characters
    
    Return Value:
        Returns an id of the message sent
    '''

    data = retrieve_data()

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")

    # Check to see if the message is too long
    if len(message) > 1000:
        raise InputError(description="The message exceeds 1000 characters")
    
    # Check to see if the given user (from token) is actully in the given channel
    user_id = auth_decode_token(token)
    if user_id not in data['channels'][channel_id]['all_members']:
        raise AccessError(description=\
            "The user corresponding to the given token is not in the channel")


    # Creating a unique id for our message_id. The chances of uuid4 returning
    # the same time is infinitesimally small.
    # ASSUMPTION: int(uuid4()) will never reproduce the same id
    unique_message_id = int(uuid4()) >> 100
    # Creating a timestamp for our time_created key for our messages dictionary
    # which is based on unix time (epoch/POSIX time)
    time_created_timestamp = round(datetime.now().timestamp())

    # Create a dictionary which we will append to our messages list in our channel
    channel_message_dictionary = {
        'message_id': unique_message_id,
        'u_id': user_id,
        'message': message,
        'time_created': time_created_timestamp,
        'reacts': [],
        'is_pinned': False,
    }

    # Create a dictionary which we will append to our data['messages'] list
    message_dictionary = {
        'message_id': unique_message_id,
        'u_id': user_id,
        'message': message,
        'time_created': time_created_timestamp,
        'channel_id': channel_id,
        'dm_id': -1,
        'is_removed': False,
        'was_shared': False,
        'reacts': [],
        'is_pinned': False,
    }

    # Append our dictionaries to their appropriate lists
    data['channels'][channel_id]['messages'].append(channel_message_dictionary)
    data['messages'].append(message_dictionary)
    
    # Create notification if someone is tagged
    tag = re.search("@[a-zA-Z1-9]*", message)
    if tag != None:
        tag = tag.group()
        tag = tag[1:]
        tagged = 0
        
        # Search for the tagged user within all_members and get their auth_id
        for member in data['channels'][channel_id]['all_members']:
            if (tag == data['users'][member]['handle_str']):
                tagged = member

        if tagged == 0: return {'message_id': unique_message_id}
        
        data['users'][tagged]['notifications'].append({
            'channel_id' : channel_id,
            'dm_id' : -1,
            'notification_message' : (str(data['users'][user_id]['handle_str'])
            + " tagged you in " + str(data['channels'][channel_id]['name'])
            + ": " + message[0:20])
        })
        # Make sure notification list is len 20
        if len(data['users'][tagged]['notifications']) > 20:
            data['users'][tagged]['notifications'].pop(0)

    return {
        'message_id': unique_message_id
    }
    

def message_remove_v1(token, message_id):
    '''
    BRIEF DESCRIPTION
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        token(string)          - User that sends the messages
        message_id(integer)    - The id of the message

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the message with message_id was not sent by the authorised user making this request
        AccessError - Occurs when the authorised user is not an owner of this channel (if it was sent to a channel) or the **Dreams**
        InputError  - Occurs when the message (based on ID) no longer exists
    
    Return Value:
        n/a
    '''

    data = retrieve_data()

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError("The given token is not valid")

    # Check if the message_id given is already deleted
    for message_dict in data['messages']:
        if message_dict['message_id'] == message_id:
            if message_dict['is_removed'] == True:
                raise InputError(description="Message (based on id) no longer exists")
    

    # Check to see if the user trying to edit the message was the one who sent it
    # or if they are an owner of the channel/dm or dreams
    AccessErrorConditions = check_access_error_conditions(token, message_id)
    if not any(AccessErrorConditions):
        raise AccessError(description=\
            "User is not dreams owner or channel owner and did not send the message")

    for msg in data['messages']:
        if msg['message_id'] == message_id:
            msg['is_removed'] = True

    return { }


def message_edit_v2(token, message_id, message):
    '''
    BRIEF DESCRIPTION
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.

    Arguments:
        token(string)           - User that sends the messages
        message_id(integer)     - The id of the original message
        message(string)         - Message content to be edited in 

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the message with message_id was not sent by the authorised user making this request
        AccessError - Occurs when the authorised user is not an owner of this channel (if it was sent to a channel) or the **Dreams**
        InputError  - Occurs when the length of message is over 1000 characters
        InputError  - Occurs when message_id refers to a deleted message
    
    Return Value:
        n/a
    '''

    data = retrieve_data()

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError("The given token is not valid")

    # Check if the message_id given is already deleted
    for message_dict in data['messages']:
        if message_dict['message_id'] == message_id:
            if message_dict['is_removed'] == True:
                raise InputError(description="Message (based on id) no longer exists")

    # Check if the message is within the character limits
    if len(message) > 1000:
        raise InputError(description="The message exceeds 1000 characters")

    # Check to see if the user trying to edit the message was the one who sent it
    # or if they are an owner of the channel/dm or dreams
    AccessErrorConditions = check_access_error_conditions(token, message_id)
    if not any(AccessErrorConditions):
        raise AccessError(description=\
            "User is not dreams owner or channel owner and did not send the message")
    

    # Remove the message if the new message is an empty string
    if message == "":
        message_remove_v1(token, message_id)
    
    # Otherwise, update the message in both data['messages'] and the channel or dm
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            channel_id = msg['channel_id']
            dms_id = msg['dm_id']
            msg['message'] = message
    if channel_id != -1:
        for ch_msg in data['channels'][channel_id]['messages']:
            if ch_msg['message_id'] == message_id:
                ch_msg['message'] = message
    else:
        for dm_msg in data['dms'][dms_id]['messages']:
            if dm_msg['message_id'] == message_id:
                dm_msg['message'] = message

    return { }


def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    BRIEF DESCRIPTION
    Share an existing message to a channel or dm.

    Arguments:
        token (string)             - User that sends the messages
        og_message_id (integer)    - The original message
        message (string)           - The optional message in addition to the shared message, and will be an empty string '' if no message is given
        channel_id (integer)       - The channel that the message is being shared to, and is -1 if it is being sent to a DM.
        dm_id (integer)            - The dm that the message is being shared to, and is -1 if it is being sent to a channel.

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the message with message_id was sent by the authorised user making this request
        AccessError - Occurs when the authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams**
        InputError  - Occurs when the length of message is over 1000 characters
        InputError  - Occurs when the message_id refers to a deleted message
    
    Return Value:
        Returns an id of the shared message
    '''

    data = retrieve_data()

    u_id = auth_decode_token(token)
    og_message = get_message(og_message_id)

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")

    # Check if the user is actually in the channel/dm they are trying to share to
    if channel_id != -1 and u_id not in data['channels'][channel_id]['all_members']:
        raise AccessError(description=\
            "User is not in the channel that they are trying to share to")
    if dm_id != -1 and u_id not in data['dms'][dm_id]['members']:
        raise AccessError(description=\
            "User is not in the channel that they are trying to share to")

    if not get_share_status(og_message_id):
        shared_message = message + '\n\n"""\n' + og_message + '\n"""'
    else:
        shared_message = message + '\n\n"""\n' + tab_given_message(og_message) + '\n"""'

    if channel_id != -1:
        shared_message_id = message_send_v2(token, channel_id, shared_message)['message_id']
        data['messages'][len(data['messages']) - 1]['was_shared'] = True
    else:
        shared_message_id = message_senddm_v1(token, dm_id, shared_message)['message_id']
        data['messages'][len(data['messages']) - 1]['was_shared'] = True


    return {'shared_message_id': shared_message_id}


# Send a message from a token to a dm_id
def message_senddm_v1(token, dm_id, message):
    '''
    BRIEF DESCRIPTION
    Send a message from authorised_user to the DM specified by dm_id. 
    Note: Each message should have it's own unique ID. I.E. No messages should share an 
    ID with another message, even if that other message is in a different channel or DM.

    Arguments:
        token (string)          - User that sends the messages
        dm_id (integer)         - The dm that the message is being sent to
        message (string)        - Message content

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the authorised user is not a member of the DM they are trying to post to
        InputError  - Occurs when the length of message is over 1000 characters
    
    Return Value:
        Returns a message id of the message sent
    '''

    data = retrieve_data()

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")

    # Check to see if the message is too long
    if len(message) > 1000:
        raise InputError(description="The message exceeds 1000 characters")
    
    # Check to see if the given user (from token) is actully in the given dm
    user_id = auth_decode_token(token)
    if user_id not in data['dms'][dm_id]['members']:
        raise AccessError(description=\
            "The user corresponding to the given token is not in the dm")

    # Create a unique id for our message_id
    unique_message_id = int(uuid4()) >> 100
    # Create a timestamp for our time_created key for our messages dictionary
    # which is based on unix time (epoch/POSIX time)
    time_created_timestamp = round(datetime.now().timestamp())

    # Create a dictionary which we will append to our messages list in our dm
    dm_message_dictionary = {
        'message_id': unique_message_id,
        'u_id': user_id,
        'message': message,
        'time_created': time_created_timestamp,
        'reacts': [],
        'is_pinned': False,
    }

    # Create a dictionary which we will append to our data['messages'] list
    message_dictionary = {
        'message_id': unique_message_id,
        'u_id': user_id,
        'message': message,
        'time_created': time_created_timestamp,
        'channel_id': -1,
        'dm_id': dm_id,
        'is_removed': False,
        'was_shared': False,
        'reacts': [],
        'is_pinned': False,
    }

    # Append our dictionaries to their appropriate lists
    data['dms'][dm_id]['messages'].append(dm_message_dictionary)
    data['messages'].append(message_dictionary)

    # Create notification if someone is tagged
    tag = re.search("@[a-zA-Z1-9]*", message)
    if tag != None:
        tag = tag.group()
        tag = tag[1:]
        tagged = 0

        # Search for the tagged user within all_members and get their auth_id
        for member in data['dms'][dm_id]['members']:
            if (tag == data['users'][member]['handle_str']):
                tagged = member
        
        notification = {
            'channel_id' : -1,
            'dm_id' : dm_id,
            'notification_message' : (str(data['users'][user_id]['handle_str'])
            + " tagged you in " + str(data['dms'][dm_id]['name'])
            + ": " + str(message[0:20]))
        }
        # Make sure notification list is len 20
        if len(data['users'][tagged]['notifications']) == 20:
            data['users'][tagged]['notifications'].pop(0)
        # Append new notification to end of list
        data['users'][tagged]['notifications'].append(notification)


    return {
        'message_id': unique_message_id
    }

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    BRIEF DESCRIPTION
    Send a message from authorised_user to the channel specified by channel_id at a
    time specified at time_sent.

    Arguments:
        token (string)          - User that sends the messages
        channel_id (integer)    - The channel that the message is being sent to
        message (string)        - Message content
        time_sent (integer)     - The time (in the future) that the message is going to be sent at

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the authorised user has not joined the channel they are trying to post to
        InputError  - Occurs when the length of message is over 1000 characters
        InputError  - Occurs when the channel_id is not a valid channel
        InputError  - Occurs when the time_sent is in the past
    
    Return Value:
        Returns a message id (integer) of the message sent
    '''

    data = retrieve_data()
    user_id = auth_decode_token(token)

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")
    
    # Checks if given channel_id is valid
    if channel_id not in data['channels']:
        raise InputError(description="The inputted channel is not a valid channel")
    
    # Check to see if the message is too long
    if len(message) > 1000:
        raise InputError(description="The message exceeds 1000 characters")
    
    if time_sent < datetime.now().timestamp():
        raise InputError(description="You can't send a message to the past")
    
    # Check to see if the given user (from token) is actully in the given channel
    if user_id not in data['channels'][channel_id]['all_members']:
        raise AccessError(description=\
            "The user corresponding to the given token is not in the channel")

    unique_message_id = int(uuid4()) >> 100

    time_until_send = round(time_sent - datetime.now().timestamp())

    # Start a timer which only performs the helper function after time_until_send seconds occur
    sendlater = threading.Timer(time_until_send, message_sendlater_channel_helper,
                                args=[user_id, channel_id, unique_message_id, message])
    sendlater.start()

    return {'message_id': unique_message_id}


def message_sendlater_channel_helper(user_id, channel_id, unique_message_id, message):
    data = retrieve_data()
    
    message_dictionary = {
        'message_id': unique_message_id,
        'u_id': user_id,
        'message': message,
        'time_created': round(datetime.now().timestamp()),
        'channel_id': channel_id,
        'dm_id': -1,
        'is_removed': False,
        'was_shared': False,
        'reacts': [{
            'react_id': 1,
            'u_ids': [],
            'is_this_user_reacted': False
        }],
        'is_pinned': False
    }

    data['messages'].append(message_dictionary)

    channel_message_dictionary = {
        'message_id': unique_message_id,
        'u_id': user_id,
        'message': message,
        'time_created': round(datetime.now().timestamp()),
        'reacts': [{
            'react_id': 1,
            'u_ids': [],
            'is_this_user_reacted': False
        }],
        'is_pinned': False
    }

    for msg in data['messages']:
        if unique_message_id == msg['message_id']:
            data['channels'][channel_id]['messages'].append(channel_message_dictionary)
    
    return {}


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    BRIEF DESCRIPTION
    Send a message from authorised_user to the dm specified by dm_id at a
    time specified by time_sent.

    Arguments:
        token (string)          - User that sends the messages
        dm_id (integer)         - The dm that the message is being sent to
        message (string)        - Message content
        time_sent (integer)     - The time (in the future) that the message is going to be sent at

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the authorised user has not joined the dm they are trying to post to
        InputError  - Occurs when the length of message is over 1000 characters
        InputError  - Occurs when the dm_id is not a valid dm
        InputError  - Occurs when the time_sent is in the past
    
    Return Value:
        Returns a message id (integer) of the message sent
    '''

    data = retrieve_data()
    user_id = auth_decode_token(token)

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")
    
    # Checks if given dm_id is valid
    if dm_id not in data['dms']:
        raise InputError(description="The inputted dm is not a valid dm")
    
    # Check to see if the message is too long
    if len(message) > 1000:
        raise InputError(description="The message exceeds 1000 characters")
    
    if time_sent < datetime.now().timestamp():
        raise InputError(description="You can't send a message to the past")
    
    # Check to see if the given user (from token) is actully in the given dm
    if user_id not in data['dms'][dm_id]['members']:
        raise AccessError(description=\
            "The user corresponding to the given token is not in the dm")

    unique_message_id = int(uuid4()) >> 100

    time_until_send = round(time_sent - datetime.now().timestamp())

    # Start a timer which only performs the helper function after time_until_send seconds occur
    sendlater = threading.Timer(time_until_send, message_sendlater_dm_helper,
                                args=[user_id, dm_id, unique_message_id, message])
    sendlater.start()

    return {'message_id': unique_message_id}


def message_sendlater_dm_helper(user_id, dm_id, unique_message_id, message):
    data = retrieve_data()
    
    message_dictionary = {
        'message_id': unique_message_id,
        'u_id': user_id,
        'message': message,
        'time_created': round(datetime.now().timestamp()),
        'channel_id': -1,
        'dm_id': dm_id,
        'is_removed': False,
        'was_shared': False,
        'reacts': [{
            'react_id': 1,
            'u_ids': [],
            'is_this_user_reacted': False
        }],
        'is_pinned': False
    }

    data['messages'].append(message_dictionary)

    dm_message_dictionary = {
        'message_id': unique_message_id,
        'u_id': user_id,
        'message': message,
        'time_created': round(datetime.now().timestamp()),
        'reacts': [{
            'react_id': 1,
            'u_ids': [],
            'is_this_user_reacted': False
        }],
        'is_pinned': False
    }

    for msg in data['messages']:
        if unique_message_id == msg['message_id']:
            data['dms'][dm_id]['messages'].append(dm_message_dictionary)
    
    return {}



def message_pin_v1(token, message_id):
    '''
    BRIEF DESCRIPTION
    The owner of a channel/dm pins a message (given by message_id) so that it
    has special display treatment in the frontend. It is pinned by setting the
    pinned flag to true.

    Arguments:
        token (string)          - User that sends the messages
        message_id (integer)    - The message id of the message to be pinned

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the authorised user is not a member of the channel/dm that the message is within
        AccessError - Occurs when the authorised user is not an owner of channel/dm
        InputError  - Occurs when the given message_id does not refer to a valid message
        InputError  - Occurs when the given message_id is already pinned
    
    Return Value:
        N/A
    '''

    data = retrieve_data()

    user_id = auth_decode_token(token)

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")

    # Check to see that the message refers to a valid message
    if not check_message_existence(message_id):
        raise InputError(description="You can't pin a message that doesn't exist")
    
    # Check to see that the message is not already pinned
    if check_message_pin_status(message_id):
        raise InputError(description="You can't pin a message that is already pinned")

    # Check to see if the given user (from token) is actully in the channel/dm of a given message.
    # Also, check to see if the given user is actually an owner of the channel/dm of a given msg
    channel_id = get_channel_id(message_id)
    dm_id = get_dm_id(message_id)
    if channel_id != -1:
        if user_id not in data['channels'][channel_id]['all_members']:
            raise AccessError(description=\
                "The user corresponding to the given token is not in the channel")
        elif user_id not in data['channels'][channel_id]['owner_members']:
            raise AccessError(description=\
                "The user corresponding to the given token is not an owner of the channel")
    else:
        if user_id not in data['dms'][dm_id]['members']:
            raise AccessError(description=\
                "The user corresponding to the given token is not in the dm")
        elif user_id != data['dms'][dm_id]['members'][0]:
            raise AccessError(description=\
                "The user corresponding to the given token is not the owner of the dm")

    # Mark the message as pinned on the messages list of data
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            msg['is_pinned'] = True
            ch_id = msg['channel_id']
            dm_id = msg['dm_id']
    
    # Mark the message as pinned on the messages list of its corresponding
    # channel of dm
    if ch_id != -1:
        for msg_channel in data['channels'][ch_id]['messages']:
            if msg_channel['message_id'] == message_id:
                msg_channel['is_pinned'] = True
    else:
        for msg_dm in data['dms'][dm_id]['messages']:
            if msg_dm['message_id'] == message_id:
                msg_dm['is_pinned'] = True
    
    return {}




def message_unpin_v1(token, message_id):
    '''
    BRIEF DESCRIPTION
    The owner of a channel/dm unpins a message (given by message_id) so that it
    no longer has special display treatment in the frontend. It is unpinned by
    setting the pinned flag to false.

    Arguments:
        token (string)          - User that sends the messages
        message_id (integer)    - The message id of the message to be pinned

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the authorised user is not a member of the channel/dm that the message is within
        AccessError - Occurs when the authorised user is not an owner of channel/dm
        InputError  - Occurs when the given message_id does not refer to a valid message
        InputError  - Occurs when the given message_id is already unpinned
    
    Return Value:
        N/A
    '''

    data = retrieve_data()

    user_id = auth_decode_token(token)

    # Check to see if token is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")

    # Check to see that the message refers to a valid message
    if not check_message_existence(message_id):
        raise InputError(description="You can't unpin a message that doesn't exist")
    
    # Check to see that the message is not already unpinned
    if not check_message_pin_status(message_id):
        raise InputError(description="You can't unpin a message that is already unpinned")

    # Check to see if the given user (from token) is actully in the channel/dm of a given message.
    # Also, check to see if the given user is actually an owner of the channel/dm of a given msg
    channel_id = get_channel_id(message_id)
    dm_id = get_dm_id(message_id)
    if channel_id != -1:
        if user_id not in data['channels'][channel_id]['all_members']:
            raise AccessError(description=\
                "The user corresponding to the given token is not in the channel")
        elif user_id not in data['channels'][channel_id]['owner_members']:
            raise AccessError(description=\
                "The user corresponding to the given token is not an owner of the channel")
    else:
        if user_id not in data['dms'][dm_id]['members']:
            raise AccessError(description=\
                "The user corresponding to the given token is not in the dm")
        elif user_id != data['dms'][dm_id]['members'][0]:
            raise AccessError(description=\
                "The user corresponding to the given token is not the owner of the dm")

    # Mark the message as pinned on the messages list of data
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            msg['is_pinned'] = False
            ch_id = msg['channel_id']
            dm_id = msg['dm_id']
    
    # Mark the message as pinned on the messages list of its corresponding
    # channel of dm
    if ch_id != -1:
        for msg_channel in data['channels'][ch_id]['messages']:
            if msg_channel['message_id'] == message_id:
                msg_channel['is_pinned'] = False
    else:
        for msg_dm in data['dms'][dm_id]['messages']:
            if msg_dm['message_id'] == message_id:
                msg_dm['is_pinned'] = False
    
    return {}
# Create or add to a reaction to a message in channel/dm
def message_react_v1(token, message_id, react_id):
    '''
    BRIEF DESCRIPTION
    Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message

    Arguments:
        token (string)          - User that reacts to the messages
        message_id (integer)    - The message id of the message being reacted
        react_id (integer)      - The react id of the reaction

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the authorised user is not a member of channel/dm that message is in
        InputError  - Occurs when the given message_id does not refer to a valid message
        InputError  - Occurs when the given message_id is already reacted
        InputError  - Occurs when the given react_id is invalid

    Return Value:
        N/A
    '''
    data = retrieve_data()

    # Make sure user is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")

    user_id = auth_decode_token(token)

    # Check to see if message_id exists in an existing channel
    found = 0
    for message in data['messages']:
        # If the message_id exists and is valid, copy important information
        if message['message_id'] == message_id:
            channel_id = message['channel_id']
            dm_id = message['dm_id']
            owner = message['u_id']
            msg = message
            found = 1
            break

    # If it doesn't exist, raise error
    if found == 0:
        raise InputError(description="The given message_id is not valid")

    # Check to see if user is authorised to react to the message (is in channel/dm)
    if not channel_id == -1:
        if user_id not in data['channels'][channel_id]['all_members']:
            raise AccessError(description="The reacting user is not a member of the messages channel")
    
    if not dm_id == -1:
        if user_id not in data['dms'][dm_id]['members']:
            raise AccessError(description="The reacting user is not a member of the messages dm")

    # Check to see if the react_id denotes a valid entry in the react library
    # Only react_id = 1 (like) is implemented
    if react_id != 1:
        raise InputError(description="The react_id is not valid")

    # Check to see if there has been an identical reaction from the user
    if len(msg['reacts']) != 0:
        for i in msg['reacts']:
            for j in i['u_ids']:
                if (j == user_id and i['react_id'] == react_id):
                    raise InputError(description="User already has identical active reaction on message")

    # If not found append a new reaction to the message and send a notification

    # Add the reaction
    # If the first to react with this react_id, create and append a reaction
    if len(msg['reacts']) == 0:
        reaction_dict = {
            'react_id': react_id,
            'u_ids': [user_id],
            'is_this_user_reacted': False,
            }
        msg['reacts'].append(reaction_dict)
        if channel_id != -1:
            for messages in data['channels'][channel_id]['messages']:
                if messages['message_id'] == message_id:
                    messages['reacts'].append(reaction_dict)
        else:
            for messages in data['dms'][dm_id]['messages']:
                if messages['message_id'] == message_id:
                    messages['reacts'].append(reaction_dict)
    # Otherwise just add to u_ids list
    else:
        msg['reacts'][0]['u_ids'].append(user_id)
    
    # Create notification message based on whether react was in dm or channel
    if channel_id != -1:
        notification_message = (str(data['users'][user_id]['handle_str']) + " reacted to your message in " + str(data['channels'][channel_id]['name']))
    else:
        notification_message = (str(data['users'][user_id]['handle_str']) + " reacted to your message in " + str(data['dms'][dm_id]['name']))
    
    # Create notification for user being reacted to
    data['users'][owner]['notifications'].append({
        'channel_id' : channel_id,
        'dm_id' : dm_id,
        'notification_message' : notification_message
    })
    # Make sure notification list is len 20
    if len(data['users'][owner]['notifications']) > 20:
        data['users'][owner]['notifications'].pop(0)

    return { }


# Deactivate a reaction in a message
def message_unreact_v1(token, message_id, react_id):
    '''
    BRIEF DESCRIPTION
    Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message

    Arguments:
        token (string)          - User that unreacts to the messages
        message_id (integer)    - The message id of the message being unreacted
        react_id (integer)      - The react id of the unreaction

    Exceptions:
        AccessError - Occurs when the token passed in is not valid
        AccessError - Occurs when the authorised user is not a member of channel/dm that message is in
        InputError  - Occurs when the given message_id does not refer to a valid message
        InputError  - Occurs when the given reaction doesn't exist
        InputError  - Occurs when the given react_id is invalid

    Return Value:
        N/A
    '''
    
    data = retrieve_data()

    # Make sure user is valid
    if not auth_token_ok(token):
        raise AccessError(description="The given token is not valid")

    user_id = auth_decode_token(token)

    # Check to see if message_id exists in an existing channel
    found = 0
    for message in data['messages']:
        # If the message_id exists and is valid, copy important information
        if message['message_id'] == message_id:
            channel_id = message['channel_id']
            dm_id = message['dm_id']
            msg = message
            found = 1


    # If it doesn't exist, raise error
    if found == 0:
        raise InputError(description="The given message_id is not valid")

    # Check to see if user is authorised to react to the message (is in channel/dm)
    if not channel_id == -1:
        if user_id not in data['channels'][channel_id]['all_members']:
            raise AccessError(description="The reacting user is not a member of the messages channel")
    
    if not dm_id == -1:
        if user_id not in data['dms'][dm_id]['members']:
            raise AccessError(description="The reacting user is not a member of the messages dm")

    # Check to see if the react_id denotes a valid entry in the react library
    # Only react_id = 1 (like) is implemented
    if react_id != 1:
        raise InputError(description="The react_id is not valid")

    # If message has no reacts whatsoever
    if len(msg['reacts']) == 0:
        raise InputError(description="User already has no reaction of the same type on message")
    # Check to see if there has been an identical reaction from the user
    else:
        for i in msg['reacts']:
            for j in i['u_ids']:
                if (j == user_id and i['react_id'] == react_id):
                    i['u_ids'].remove(user_id)
                    # Delete react element if last u_id on the u_ids list
                    if len(i['u_ids']) == 0: {
                        msg['reacts'].clear()
                    }
                    return {}

    # If not found, return an error, because we're not creating a new react
    # we don't need to send a notification
    raise InputError(description="User already has no reaction of the same type on message")


###############################################################################
#                                END FUNCTIONS                                #
###############################################################################




###############################################################################
#                               HELPER FUNCTIONS                              #
###############################################################################

# Given a message_id return the channel in which it was sent
def get_channel_id(message_id):
    data = retrieve_data()
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            ch_id = msg['channel_id']
    return ch_id

# Given a message_id return the dm in which it was sent
def get_dm_id(message_id):
    data = retrieve_data()
    dm_id = -1
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            dm_id = msg["dm_id"]
    return dm_id


# Given a message_id return the message within that message_id
def get_message(message_id):
    data = retrieve_data()
    message = ""
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            message = msg["message"]
    return message

# Given a message_id, return whether the message is a shared message or not
def get_share_status(message_id):
    data = retrieve_data()
    share_status = False
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            share_status = msg['was_shared']
    return share_status


# Given a message, return a tab in front of the relevant lines
def tab_given_message(msg):
    index = 0
    flag = 0
    for n in range(0, len(msg) - 2):
        if msg[n] == msg[n + 1] == msg[n + 2] == '"':
            if flag != 2:
                flag = 1
        if flag == 1:
            index = n - 2
            flag = 2
    beginning_of_string = msg[0:index]
    to_be_changed_str = msg[index:]
    changed_string = to_be_changed_str.replace("\n", "\n\t")

    tabbed_msg = beginning_of_string + changed_string
    return tabbed_msg


# Given a message_id, check if the message refers to a valid message
def check_message_existence(message_id):
    data = retrieve_data()
    message_exists = False
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            # Check to see if the message has been removed previously
            if msg['is_removed'] == False:
                message_exists = True
    return message_exists


# Given a message_id, check if the message is pinned
def check_message_pin_status(message_id):
    data = retrieve_data()
    pin_status = 0
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            # Check to see if the message has been removed previously
            if msg['is_pinned'] == True:
                pin_status = 1
    if pin_status == 1:
        return True
    else:
        return False


# Check for the access error conditions of message remove and message edit
def check_access_error_conditions(token, message_id):
    data = retrieve_data()
    given_id = auth_decode_token(token)
    did_user_send, is_ch_owner, is_dm_owner, is_dreams_owner, is_owner = True, False, False, False, False
    for msg_dict in data['messages']:
        if msg_dict['message_id'] == message_id:
            if msg_dict['u_id'] != given_id:
                did_user_send = False
    # Now, check to see if the user is an owner of the channel
    ch_id = get_channel_id(message_id)
    dm_id = get_dm_id(message_id)
    if ch_id != -1:
        for member in data['channels'][ch_id]['owner_members']:
            if given_id == member:
                is_ch_owner = True
    else:
        if given_id == data['dms'][dm_id]['members'][0]:
            is_dm_owner = True
    # Now, check to see if the user is an owner of dreams server
    if data['users'][given_id]['permission_id'] == 1:
        is_dreams_owner = True
    if is_ch_owner or is_dreams_owner or is_dm_owner:
        is_owner = True
    AccessErrorConditions = [is_owner, did_user_send]
    
    return AccessErrorConditions
