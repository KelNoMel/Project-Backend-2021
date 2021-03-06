# PROJECT-BACKEND: Team Echo
# Written by Brendan Ye

import pytest

from src.error import InputError, AccessError
from src.channel import channel_messages_v2, channel_invite_v2
from src.auth import auth_register_v1
from src.channels import channels_create_v2
from src.message import message_send_v2, message_remove_v1, message_senddm_v1
from src.other import clear_v1
from src.dm import dm_create_v1, dm_messages_v1


###############################################################################
#                                 ASSUMPTIONS                                 #
###############################################################################

# "Removing" a message just removes the text from the message and tags the
# message as removed

# It is impossible for a user to "remove" a message when there are no messages
# in the channel/dm (meaning nothing at all, not as in all messages are removed)

###############################################################################
#                               HELPER FUNCTIONS                              #
###############################################################################

# User sends x messages
def send_x_messages(user, channel, num_messages):
    message_count = 0
    messages_list = []
    while message_count < num_messages:
        message_num = message_count + 1
        m_id = message_send_v2(user["token"], channel, str(message_num))
        messages_list.append(m_id)
        message_count += 1
    
    return messages_list

# User removes x messages
def remove_x_messages(user, id_list=[]):
    message_count = 0
    while message_count < len(id_list):
        message_remove_v1(user["token"], id_list[message_count])
        message_count += 1
    
    return {}



###############################################################################
#                                   TESTING                                   #
###############################################################################

############################# EXCEPTION TESTING ##############################

# Access error when the user trying to remove the message did not send the
# message OR is not an owner of the channel/dreams
def test_message_remove_v1_AccessError(set_up_message_data):
    setup = set_up_message_data
    user1, user2, channel1 = setup['user1'], setup['user2'], setup['channel1']

    m_id = message_send_v2(user1["token"], channel1, "Hello")['message_id']
    
    # user2 who did not send the message with m_id tries to remove the message 
    # - should raise an access error as they are not owner/dreams member
    with pytest.raises(AccessError):
        assert message_remove_v1(user2["token"], m_id)


# Input error when the message_id has already been removed
def test_message_remove_v1_InputError(set_up_message_data):
    setup = set_up_message_data
    user1, channel1 = setup['user1'], setup['channel1']
    
    m_id2 = message_send_v2(user1["token"], channel1, "Hello")['message_id']

    message_remove_v1(user1["token"], m_id2)

    with pytest.raises(InputError):
        assert message_remove_v1(user1["token"], m_id2)

def test_message_remove_v1_AccessError_not_dm_owner(set_up_message_data):
    setup = set_up_message_data
    user1, user2, dm1 = setup['user1'], setup['user2'], setup['dm1']

    m_id = message_senddm_v1(user1["token"], dm1, "Hello")['message_id']
    
    # user2 who did not send the message with m_id tries to remove the message 
    # - should raise an access error as they are not owner/dreams member
    with pytest.raises(AccessError):
        assert message_remove_v1(user2["token"], m_id)

# Default access error when token is invalid
def test_message_remove_v1_default_Access_Error():

    with pytest.raises(AccessError):
        message_remove_v1("invalid token", 123)


############################ END EXCEPTION TESTING ############################


########################### TESTING MESSAGE REMOVE ############################


# Testing the removal of 1 message by user2
def test_message_remove_v1_remove_one(set_up_message_data):
    setup = set_up_message_data
    user1, user2, channel1 = setup['user1'], setup['user2'], setup['channel1']

    # Send 3 messages and remove the very first message sent
    msgs_list = send_x_messages(user2, channel1, 3)
    
    channel_msgs = channel_messages_v2(user1["token"], channel1, 0)
    
    m_id = msgs_list[0]['message_id']
    message_remove_v1(user2["token"], m_id)

    m_dict1 = channel_msgs['messages'][1]
    m_dict2 = channel_msgs['messages'][0]
    
    answer = {
        'messages': [m_dict2, m_dict1],
        'start': 0,
        'end': -1
    }

    assert channel_messages_v2(user1["token"], channel1, 0) == answer


# Testing the removal of multiple messages
def test_message_remove_v1_remove_multiple(set_up_message_data):
    setup = set_up_message_data
    user1, user2, channel1 = setup['user1'], setup['user2'], setup['channel1']

    # Send 5 messages and remove messages with index 0, 2, 3
    msgs_list = send_x_messages(user2, channel1, 5)

    channel_msgs = channel_messages_v2(user1["token"], channel1, 0)

    m_id0 = msgs_list[0]['message_id']
    m_id2 = msgs_list[2]['message_id']
    m_id3 = msgs_list[3]['message_id']
    message_remove_v1(user2["token"], m_id0)
    message_remove_v1(user2["token"], m_id2)
    message_remove_v1(user2["token"], m_id3)

    m_dict1 = channel_msgs['messages'][3]
    m_dict4 = channel_msgs['messages'][0]

    answer = {
        'messages': [m_dict4, m_dict1],
        'start': 0,
        'end': -1
    }

    assert channel_messages_v2(user2["token"], channel1, 0) == answer


# Testing the removal of all messages in the channel
def test_message_remove_v1_remove_all(set_up_message_data):
    setup = set_up_message_data
    user1, user2, channel1 = setup['user1'], setup['user2'], setup['channel1']

    send_x_messages(user2, channel1, 25)
    channel_msgs = channel_messages_v2(user1["token"], channel1, 0)
    reversed_channel_msgs = channel_msgs["messages"][::-1]
    m_ids = [reversed_channel_msgs[i]["message_id"] for i in range(25)]

    remove_x_messages(user2, m_ids)

    answer = {
        'messages': [],
        'start': 0,
        'end': -1
    }

    assert channel_messages_v2(user2["token"], channel1, 0) == answer


# Testing the removal of a message by the owner of the channel when the owner
# didn't send the message
def test_message_remove_v1_owner_removes_message():
    clear_v1()
    user1 = auth_register_v1('bob.builder@email.com', 'badpassword1', 'Bob', 'Builder') # Dreams owner
    user2 = auth_register_v1('shaun.sheep@email.com', 'password123', 'Shaun', 'Sheep')
    user3 = auth_register_v1('thomas.tankengine@email.com', 'password123', 'Thomas', 'Tankengine')
    channel1 = channels_create_v2(user2['token'], 'Channel1', True)['channel_id']
    channel_invite_v2(user2['token'], channel1, user3['auth_user_id'])
    channel_invite_v2(user2['token'], channel1, user1['auth_user_id'])

    # user3 sends 3 messages and user2 removes the second message sent
    send_x_messages(user3, channel1, 3)
    channel_msgs = channel_messages_v2(user2["token"], channel1, 0)    

    m_id = channel_msgs["messages"][1]["message_id"]
    message_remove_v1(user2['token'], m_id)


    m_dict0 = channel_msgs['messages'][2]
    m_dict2 = channel_msgs['messages'][0]

    answer = {
        'messages': [m_dict2, m_dict0],
        'start': 0,
        'end': -1
    }

    assert channel_messages_v2(user2['token'], channel1, 0) == answer


# Testing the removal of a message by the owner of dreams when the owner did
# not send the message and is not part of the channel
def test_message_remove_v1_dream_owner_removes_message():
    clear_v1()
    user1 = auth_register_v1('bob.builder@email.com', 'badpassword1', 'Bob', 'Builder') # Dreams owner
    user2 = auth_register_v1('shaun.sheep@email.com', 'password123', 'Shaun', 'Sheep')
    user3 = auth_register_v1('thomas.tankengine@email.com', 'password123', 'Thomas', 'Tankengine')
    channel1 = channels_create_v2(user2['token'], 'Channel1', True)['channel_id']
    channel_invite_v2(user2['token'], channel1, user3['auth_user_id'])

    # user3 sends 3 messages and user1 (dreams owner) who is not in the channel
    # removes the very first message sent
    send_x_messages(user3, channel1, 3)
    channel_msgs = channel_messages_v2(user2["token"], channel1, 0)
    m_id = channel_msgs["messages"][1]["message_id"]
    message_remove_v1(user1['token'], m_id)

    m_dict0 = channel_msgs["messages"][2]
    m_dict2 = channel_msgs["messages"][0]

    answer = {
        'messages': [m_dict2, m_dict0],
        'start': 0,
        'end': -1
    }

    assert channel_messages_v2(user2['token'], channel1, 0) == answer


# Testing the removal of a message by the owner of dreams when the owner did
# not send the message and is part of the channel
def test_message_remove_v1_dream_owner_removes_message_in_channel():
    clear_v1()
    user1 = auth_register_v1('bob.builder@email.com', 'badpassword1', 'Bob', 'Builder') # Dreams owner
    user2 = auth_register_v1('shaun.sheep@email.com', 'password123', 'Shaun', 'Sheep')
    user3 = auth_register_v1('thomas.tankengine@email.com', 'password123', 'Thomas', 'Tankengine')
    channel1 = channels_create_v2(user2["token"], 'Channel1', True)['channel_id']
    channel_invite_v2(user2['token'], channel1, user3['auth_user_id'])
    channel_invite_v2(user2['token'], channel1, user1['auth_user_id'])

    # user3 sends 3 messages and user1 (dreams owner) who is in the channel
    # removes the very first message sent
    send_x_messages(user3, channel1, 3)
    channel_msgs = channel_messages_v2(user2["token"], channel1, 0)
    m_id = channel_msgs["messages"][1]["message_id"]
    message_remove_v1(user1['token'], m_id)


    m_dict0 = channel_msgs["messages"][2]
    m_dict2 = channel_msgs["messages"][0]

    answer = {
        'messages': [m_dict2, m_dict0],
        'start': 0,
        'end': -1
    }

    assert channel_messages_v2(user2['token'], channel1, 0) == answer

# Testing the removal of the same message in 2 different channels (different
# message_ids though)
def test_message_remove_v1_remove_same_msg_diff_channels(set_up_message_data):
    setup = set_up_message_data
    user2, channel1 = setup['user2'], setup['channel1']

    channel2 = channels_create_v2(user2["token"], 'Channel2', True)['channel_id']

    # Have user2 send the same message to channel1 and channel2 and then
    # remove both the messages
    message_send_v2(user2["token"], channel1, "Hello")
    message_send_v2(user2["token"], channel2, "Hello")
    channel1_msgs = channel_messages_v2(user2["token"], channel1, 0)
    channel2_msgs = channel_messages_v2(user2["token"], channel2, 0)
    
    m_id_ch1 = channel1_msgs["messages"][0]["message_id"]
    m_id_ch2 = channel2_msgs["messages"][0]["message_id"]

    message_remove_v1(user2["token"], m_id_ch1)
    message_remove_v1(user2["token"], m_id_ch2)

    ans1 = {
        'messages': [],
        'start': 0,
        'end': -1
    }
    ans2 = {
        'messages': [],
        'start': 0,
        'end': -1
    }

    assert channel_messages_v2(user2["token"], channel1, 0) == ans1
    assert channel_messages_v2(user2["token"], channel2, 0) == ans2

# Testing the removal of a message in a dm
def test_message_edit_v2_edit_msg_in_dm(set_up_message_data):
    setup = set_up_message_data
    user1, dm1 = setup['user1'], setup['dm1']

    message_count = 0
    while message_count < 5:
        message_num = message_count + 1
        message_senddm_v1(user1["token"], dm1, str(message_num))
        message_count += 1

    dm_msgs = dm_messages_v1(user1["token"], dm1, 0)

    msg0 = dm_msgs['messages'][4]
    msg2 = dm_msgs['messages'][2]
    msg3 = dm_msgs['messages'][1]
    message_remove_v1(user1["token"], msg0['message_id'])
    message_remove_v1(user1["token"], msg2['message_id'])
    message_remove_v1(user1["token"], msg3['message_id'])

    m_dict1 = dm_msgs['messages'][3]
    m_dict4 = dm_msgs['messages'][0]


    answer = {
        'messages': [m_dict4, m_dict1],
        'start': 0,
        'end': -1
    }

    assert dm_messages_v1(user1["token"], dm1, 0) == answer
