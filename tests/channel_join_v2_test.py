# PROJECT-BACKEND: Team Echo
# Written by Kellen Liew

import pytest
from src.data import retrieve_data
from src.error import InputError, AccessError

from src.auth import auth_register_v1
from src.channel import channel_join_v2, channel_details_v2
from src.channels import channels_create_v2, channels_list_v2
from src.other import clear_v1

# Helper function to set up users
def setup_users():
    clear_v1()
    user1 = auth_register_v1('example1@hotmail.com', 'password1', 'first1', 'last1')
    user2 = auth_register_v1('example2@hotmail.com', 'password2', 'first2', 'last2')
    user3 = auth_register_v1('example3@hotmail.com', 'password3', 'first3', 'last3')
    user4 = auth_register_v1('example4@hotmail.com', 'password4', 'first4', 'last4')

    return {
        'user1': user1,
        'user2': user2,
        'user3': user3,
        'user4': user4,
    }

#Cases start here

#Standard Case, pass expected
def test_standard():
    setup = setup_users()
    a_u_id1 = setup['user1']
    a_u_id2 = setup['user2']

    chid1 = channels_create_v2(a_u_id1['token'], 'channel1', True) #Public channel created
    channel_join_v2(a_u_id2['token'], chid1['channel_id']) #User 2 joins channel 1 as regular member
    
    # Expect a list containing channel 1
    assert channels_list_v2(a_u_id2['token']) == {
        'channels': [
            {
                'channel_id': chid1['channel_id'],
                'name': 'channel1',
            },
        ],
    }

#Case where a user joins multiple channels
def test_multiple_channels_joined():
    setup = setup_users()
    a_u_id1 = setup['user1']
    a_u_id2 = setup['user2']

    channels_create_v2(a_u_id1['token'], 'channel1', True) #Public channel1 created
    chid2 = channels_create_v2(a_u_id1['token'], 'channel2', True) #Public channel2 created
    chid3 = channels_create_v2(a_u_id1['token'], 'channel3', True) #Public channel3 created
    chid4 = channels_create_v2(a_u_id1['token'], 'channel4', True) #Public channel4 created
    channel_join_v2(a_u_id1['token'], chid2['channel_id']) #User 1 joins channel 1 - testing skip
    channel_join_v2(a_u_id2['token'], chid2['channel_id']) #User 2 joins channel 2 as regular member
    channel_join_v2(a_u_id2['token'], chid3['channel_id']) #User 2 joins channel 3 as regular member
    channel_join_v2(a_u_id2['token'], chid4['channel_id']) #User 2 joins channel 4 as regular member
    

    # Expecting a list containing channels 2-4
    assert channels_list_v2(a_u_id2['token']) == {
        'channels': [
            {
                'channel_id': chid2['channel_id'],
                'name': 'channel2',
            },
            {
                'channel_id': chid3['channel_id'],
                'name': 'channel3',
            },
            {
                'channel_id': chid4['channel_id'],
                'name': 'channel4',
            },
        ],
    }

#Case where multiple  join one channel
def test_multiple_joiners():
    setup = setup_users()
    a_u_id1 = setup['user1']
    a_u_id2 = setup['user2']
    a_u_id3 = setup['user3']
    a_u_id4 = setup['user4']

    chid1 = channels_create_v2(a_u_id1['token'], 'channel1', True) #Public channel1 created
    channel_join_v2(a_u_id2['token'], chid1['channel_id']) #User 2 joins channel 1 as regular member
    channel_join_v2(a_u_id3['token'], chid1['channel_id']) #User 3 joins channel 1 as regular member
    channel_join_v2(a_u_id4['token'], chid1['channel_id']) #User 4 joins channel 1 as regular member

    # Expecting a owner members including 1, and all members including 1-4
    assert channel_details_v2(a_u_id1['token'], chid1['channel_id']) == {
        'name': 'channel1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': a_u_id1['auth_user_id'],
                'email': 'example1@hotmail.com',
                'name_first': 'first1',
                'name_last': 'last1',
                'handle_str': 'first1last1'
            }
        ],
        'all_members': [
            {
                'u_id': a_u_id1['auth_user_id'],
                'email': 'example1@hotmail.com',
                'name_first': 'first1',
                'name_last': 'last1',
                'handle_str': 'first1last1'
            },
            {
                'u_id': a_u_id2['auth_user_id'],
                'email': 'example2@hotmail.com',
                'name_first': 'first2',
                'name_last': 'last2',
                'handle_str': 'first2last2'
            },
            {
                'u_id': a_u_id3['auth_user_id'],
                'email': 'example3@hotmail.com',
                'name_first': 'first3',
                'name_last': 'last3',
                'handle_str': 'first3last3'
            },
            {
                'u_id': a_u_id4['auth_user_id'],
                'email': 'example4@hotmail.com',
                'name_first': 'first4',
                'name_last': 'last4',
                'handle_str': 'first4last4'
            },
        ],
    }

#Case where user attempts to join a private channel (Access Error)
def test_private_channel():
    setup = setup_users()
    a_u_id1 = setup['user1']
    a_u_id2 = setup['user2']

    chid1 = channels_create_v2(a_u_id1['token'], 'channel1', False) #Private channel created

    with pytest.raises(AccessError):
        channel_join_v2(a_u_id2['token'], chid1['channel_id']) #Channel_id1 is a private channel

#Case where channel_join is given the id of a non-existent channel
def test_invalid_channel():
    setup = setup_users()
    a_u_id1 = setup['user1']
    a_u_id2 = setup['user2']

    channels_create_v2(a_u_id1['token'], 'channel1', True) #Public channel created

    with pytest.raises(InputError):
        channel_join_v2(a_u_id2['token'], 123) #Channel_id2 doesn't exist

#Assumptions,  who are already in a channel will not join it again