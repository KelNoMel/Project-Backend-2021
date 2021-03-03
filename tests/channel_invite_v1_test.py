import pytest
from src.data import data

from src.error import InputError
from src.error import AccessError

from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_invite_v1
from src.channel import channel_details_v1

# Include fixtures?
# After required functions are implemented

# Typical case
def test_function():
    data.clear()
    auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1') #returns auth_user_id1 e.g.
    auth_register_v1('example2@hotmail.com', 'password2', 'first_name2', 'last_name2') #returns auth_user_id2 e.g.
    channels_create_v1('auth_user_id1', 'channel1', True) #returns channel_id1 e.g.
    channel_invite_v1('auth_user_id1', 'channel_id1', 'auth_user_id2')
    assert channel_details_v1('auth_user_id2', 'channel_id1') == {
        'name': 'channel1',
        'owner_members': [
            {
                'u_id': 1,
                'name_first': 'first_name1',
                'name_last': 'last_name1',
            }
        ],
        'all_members': [
            {
                'u_id': 2,
                'name_first': 'first_name2',
                'name_last': 'last_name2',
            }
        ],
    }

# Running channel_invite multiple times
def test_multiple_runs():
    data.clear()
    auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1') #returns auth_user_id1 e.g.
    auth_register_v1('example2@hotmail.com', 'password2', 'first_name2', 'last_name2') #returns auth_user_id2 e.g.
    auth_register_v1('example3@hotmail.com', 'password3', 'first_name3', 'last_name3') #returns auth_user_id3 e.g.
    auth_register_v1('example4@hotmail.com', 'password4', 'first_name4', 'last_name4') #returns auth_user_id4 e.g.
    auth_register_v1('example5@hotmail.com', 'password5', 'first_name5', 'last_name5') #returns auth_user_id5 e.g.
    channels_create_v1('auth_user_id1', 'channel1', True) #returns channel_id1 e.g.
    channel_invite_v1('auth_user_id1', 'channel_id1', 'auth_user_id2')
    channel_invite_v1('auth_user_id1', 'channel_id1', 'auth_user_id3')
    channel_invite_v1('auth_user_id1', 'channel_id1', 'auth_user_id4')
    channel_invite_v1('auth_user_id1', 'channel_id1', 'auth_user_id5')
    assert channel_details_v1('auth_user_id2', 'channel_id1') == {
        'name': 'channel1',
        'owner_members': [
            {
                'u_id': 1,
                'name_first': 'first_name1',
                'name_last': 'last_name1',
            }
        ],
        'all_members': [
            {
                'u_id': 2,
                'name_first': 'first_name2',
                'name_last': 'last_name2',
            },
            {
                'u_id': 3,
                'name_first': 'first_name3',
                'name_last': 'last_name3',
            },
            {
                'u_id': 4,
                'name_first': 'first_name4',
                'name_last': 'last_name4',
            },
            {
                'u_id': 5,
                'name_first': 'first_name5',
                'name_last': 'last_name5',
            },
        ],
    }

# Channel_invite given channel id belonging to a non-existent channel
def test_invalid_channel_id():
    data.clear()
    auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1') #returns auth_user_id1 e.g.
    auth_register_v1('example2@hotmail.com', 'password2', 'first_name2', 'last_name2') #returns auth_user_id2 e.g.
    with pytest.raises(InputError):
        channel_invite_v1('auth_user_id1', 'channel_id1', 'auth_user_id2')

# Channel_invite given user that does not exist
def test_invalid_invited_user():
    data.clear()
    auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1') #returns auth_user_id1 e.g.
    channels_create_v1('auth_user_id1', 'channel1', True) #returns channel_id1 e.g.
    with pytest.raises(InputError):
        channel_invite_v1('auth_user_id1', 'channel_id1', 'auth_user_id2')

# Channel_invite executed by user not in given channel
def test_unauthorized_user():
    data.clear()
    auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1') #returns auth_user_id1 e.g.
    auth_register_v1('example2@hotmail.com', 'password2', 'first_name2', 'last_name2') #returns auth_user_id2 e.g.
    auth_register_v1('example3@hotmail.com', 'password3', 'first_name3', 'last_name3') #returns auth_user_id3 e.g.
    channels_create_v1('auth_user_id1', 'channel1', True) #returns channel_id1 e.g.
    with pytest.raises(AccessError):
        channel_invite_v1('auth_user_id2', 'channel_id1', 'auth_user_id3')