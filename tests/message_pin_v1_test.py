# PROJECT-BACKEND: Team Echo
# Written by Brendan Ye

import pytest

from src.error import InputError, AccessError
from src.channel import channel_messages_v2, channel_invite_v2
from src.auth import auth_register_v1
from src.channels import channels_create_v2
from src.message import message_send_v2, message_senddm_v1, message_pin_v1
from src.other import clear_v1


###############################################################################
#                               HELPER FUNCTIONS                              #
###############################################################################

# Simple data population helper function; registers users 1 and 2,
# creates channel_1 with member u_id = 1
def set_up_data():
    clear_v1()
    
    # Populate data - create/register users 1 and 2 and have user 1 make channel1
    user1 = auth_register_v1('bob.builder@email.com', 'badpassword1', 'Bob', 'Builder')
    user2 = auth_register_v1('shaun.sheep@email.com', 'password123', 'Shaun', 'Sheep')
    channel1 = channels_create_v2(user1['token'], 'Channel1', True)
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])

    setup = {
        'user1': user1,
        'user2': user2,
        'channel1': channel1['channel_id'],
        'dm1': dm1['dm_id']
    }

    return setup


def send_x_messages(user1, user2, channel1, num_messages):
    message_count = 0
    while message_count < num_messages:
        message_num = message_count + 1
        if message_count % 2 == 0:
            message_send_v2(user1["token"], channel1, str(message_num))
        else:
            message_send_v2(user2["token"], channel1, str(message_num))
        message_count += 1
    
    return {}

###############################################################################
#                                   TESTING                                   #
###############################################################################

############################# EXCEPTION TESTING ##############################
# Testing for when the user is not part of the channel
def test_message_pin_v1_AccessError():
    setup = set_up_data()
    user1, user2, channel1 = setup['user1'], setup['user2'], setup['channel1']

    m_id = message_send_v2(user1['token'], channel1, "HEY EVERYBODY")
    
    # user2 who is not a part of channel1 tries to pin message 
    # - should raise an access error
    with pytest.raises(AccessError):
        assert message_pin_v1(user2["token"], m_id["message_id"])


# Testing for when the user is not part of the dm
def test_message_pin_v1_AccessError_dm():
    setup = set_up_data()
    user1, dm1 = setup['user1'], setup['dm1']

    m_id = message_senddm_v1(user1['token'], dm1, "HEY EVERYBODY")
    user3 = auth_register_v1('thomas.tankengine@email.com', 'password12345', 'Thomas', 'Tankengine')

    # user3 who is not a part of dm1 tries to pin message 
    # - should raise an access error
    with pytest.raises(AccessError):
        assert message_pin_v1(user3["token"], m_id["message_id"])


# Testing for when the user is not an owner of the channel but is within it
def test_message_pin_v1_AccessError_non_owner():
    setup = set_up_data()
    user1, user2, channel1 = setup['user1'], setup['user2'], setup['channel1']
    channel_invite_v2(user1["token"], channel1, user2["auth_user_id"])

    m_id = message_send_v2(user1['token'], channel1, "HEY EVERYBODY")
    
    # user2 who is not a part of channel1 tries to pin message 
    # - should raise an access error
    with pytest.raises(AccessError):
        assert message_pin_v1(user2["token"], m_id["message_id"])


# Testing for when the user is not an owner of the dm but is within it
def test_message_pin_v1_AccessError_dm_non_owner():
    setup = set_up_data()
    user1, dm1 = setup['user1'], setup['dm1']

    m_id = message_senddm_v1(user1['token'], dm1, "HEY EVERYBODY")

    # user2 who is not a part of channel1 tries to pin message 
    # - should raise an access error
    with pytest.raises(AccessError):
        assert message_pin_v1(user2["token"], m_id["message_id"])


# Message id is not a real message id
def test_message_pin_v1_InputError_non_valid_id():
    setup = set_up_data()
    user1 = setup['user1']
    
    # user1 (the channel owner) tries to pin a non existent message
    with pytest.raises(AccessError):
        assert message_pin_v1(user1["token"], 742)


# Message id is already pinned
def test_message_pin_v1_InputError_already_pinned():
    setup = set_up_data()
    user1, channel1 = setup['user1'], setup['channel1']

    m_id = message_send_v2(user1['token'], channel1, "HEY EVERYBODY")
    message_pin_v1(user1["token"], m_id["message_id"])

    # user1 (the channel owner) tries to pin an already pinned message
    with pytest.raises(AccessError):
        assert message_pin_v1(user1["token"], m_id["message_id"])


# Default access error when token is invalid
def test_message_sendlater_v1_default_Access_Error():
    setup = set_up_data()
    user1, channel1 = setup['user1'], setup['channel1']

    m_id = message_send_v2(user1['token'], channel1, "Hello")

    with pytest.raises(AccessError):
        message_pin_v1("invalid token", m_id["message_id"])

############################ END EXCEPTION TESTING ############################


############################# TESTING MESSAGE PIN #############################

# Testing to see if one message is pinned correctly
def test_message_pin_v1_pin_one():
    setup = set_up_data()
    user1, channel1 = setup['user1'], setup['channel1']

    m_id = message_send_v2(user1['token'], channel1, "Hello")
    message_pin_v1(user1["token"], m_id["message_id"])

    assert len(channel_messages_v2(user1['token'], channel1, 0)['messages']) == 1
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][0]['message'] == "Hello"
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][0]['is_pinned'] == True
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][0]['message_id'] == m_id


# Testing to see if one message is pinned correctly
def test_message_pin_v1_pin_multiple():
    setup = set_up_data()
    user1, channel1 = setup['user1'], setup['channel1']
    channel_invite_v2(user1["token"], channel1, user2["auth_user_id"])

    m_id1 = message_send_v2(user1['token'], channel1, "Hello")
    message_pin_v1(user1["token"], m_id1["message_id"])

    send_x_messages(user1, user2, channel1, 20)

    m_id2 = message_send_v2(user2['token'], channel1, "Bao")
    m_id3 = message_send_v2(user1['token'], channel1, "Bye")
    message_pin_v1(user1["token"], m_id2["message_id"])

    assert len(channel_messages_v2(user1['token'], channel1, 0)['messages']) == 23
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][22]['message'] == "Hello"
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][22]['is_pinned'] == True
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][22]['message_id'] == m_id1
    
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][1]['message'] == "Bao"
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][1]['is_pinned'] == True
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][1]['message_id'] == m_id2
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][1]['u_id'] == user2["auth_user_id"]

    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][2]['message'] == "20"
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][2]['is_pinned'] == False

    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][0]['message'] == "Bye"
    assert channel_messages_v2(user1['token'], channel1, 0)['messages'][0]['is_pinned'] == False


# Testing to see if one message is pinned correctly to a dm
def test_message_pin_v1_pin_one_dm():
    setup = set_up_data()
    user1, dm1 = setup['user1'], setup['dm1']

    m_id = message_senddm_v1(user1['token'], dm1, "Hello")
    message_pin_v1(user1["token"], m_id["message_id"])

    assert len(channel_messages_v1(user1['token'], dm1, 0)['messages']) == 1
    assert dm_messages_v1(user1['token'], dm1, 0)['messages'][0]['message'] == "Hello"
    assert dm_messages_v1(user1['token'], dm1, 0)['messages'][0]['is_pinned'] == True
    assert dm_messages_v1(user1['token'], dm1, 0)['messages'][0]['message_id'] == m_id