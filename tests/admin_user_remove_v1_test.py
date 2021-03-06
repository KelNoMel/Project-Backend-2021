# PROJECT-BACKEND: Team Echo
# Written by Nikki Yao

import pytest

from src.channel import channel_join_v2, channel_messages_v2, channel_addowner_v1, channel_details_v2, channel_invite_v2
from src.channels import channels_create_v2
from src.error import InputError, AccessError
from src.dm import dm_create_v1, dm_messages_v1, dm_details_v1, dm_invite_v1
from src.message import message_send_v2, message_senddm_v1
from src.other import admin_user_remove_v1, admin_userpermission_change_v1
from src.user import user_profile_v2

######################### Tests admin_user_remove ########################
                                                         
#   * uses pytest fixtures from src.conftest                                    
                                                                                                                                                
##########################################################################


# Checks invalid token
def test_admin_user_remove_invalid_token(setup_user):
    users = setup_user

    with pytest.raises(AccessError):
        admin_user_remove_v1("Invalid owner", users['user1']['auth_user_id'])


# Checks invalid auth_user_id
def test_admin_user_remove_invalid_uid(setup_user):
    users = setup_user
    
    with pytest.raises(InputError):
        admin_user_remove_v1(users['user1']['token'], "Invalid user")


# Checks invalid owner access
def test_admin_user_remove_invalid_owner(setup_user):
    users = setup_user

    with pytest.raises(AccessError):
        admin_user_remove_v1(users['user2']['token'], users['user1']['auth_user_id'])


# Checks invalid removal as user is the only owner
def test_admin_user_remove_only_owner(setup_user):
    users = setup_user

    with pytest.raises(InputError):
        admin_user_remove_v1(users['user1']['token'], users['user1']['auth_user_id'])


# Asserts that user_profile, channel_messages, dm_messages are changed to 'Removed user'
def test_admin_user_remove_only_channel_owner(setup_user):
    users = setup_user

    dm_create_v1(users['user5']['token'],[users['user4']['auth_user_id'],users['user3']['auth_user_id']])

    # User 1 makes channel 1 
    channel_id1 = channels_create_v2(users['user1']['token'],'Test Channel',True)
    # User 3 joins the public channel
    channel_join_v2(users['user3']['token'], channel_id1['channel_id'])
    # User 1 makes User 3 an owner
    channel_addowner_v1(users['user1']['token'], channel_id1['channel_id'], users['user3']['auth_user_id'])
    # User 1 sends a message
    message_send_v2(users['user1']['token'],channel_id1['channel_id'],'Nice day')

    # User 2 makes channel 2 
    channel_id2 = channels_create_v2(users['user2']['token'],'Test Channel',False)
    # User 1 joins the private channel as global owner
    channel_join_v2(users['user1']['token'], channel_id2['channel_id'])
    # User 1 sends a message
    message_send_v2(users['user1']['token'],channel_id2['channel_id'],'Hello user2')

    # User 1 creates a dm to User 2 and User 3. User 1 sends a message
    dm_id1 = dm_create_v1(users['user1']['token'],[users['user2']['auth_user_id'],users['user3']['auth_user_id']])
    message_senddm_v1(users['user1']['token'],dm_id1['dm_id'],'Hi guys')

    # Set up variables to test function outputs
    user_profile_id1 = user_profile_v2(users['user2']['token'],users['user1']['auth_user_id'])
    messages_channel_id1 = channel_messages_v2(users['user3']['token'],channel_id1['channel_id'],0)
    messages_channel_id2 = channel_messages_v2(users['user2']['token'],channel_id2['channel_id'],0)
    messages_dm_id_1 = dm_messages_v1(users['user2']['token'],dm_id1['dm_id'],0)

    # Ensure the correct output
    assert user_profile_id1['user']['name_first'] == "user1_first"
    assert messages_channel_id1['messages'][0]['message'] == "Nice day"
    assert messages_channel_id2['messages'][0]['message'] == "Hello user2"
    assert messages_dm_id_1['messages'][0]['message'] == "Hi guys"
    
    # Global User 2 removes Global User 1
    admin_userpermission_change_v1(users['user1']['token'], users['user2']['auth_user_id'], 1)
    admin_userpermission_change_v1(users['user2']['token'], users['user3']['auth_user_id'], 1)   
    # Function called 
    admin_user_remove_v1(users['user2']['token'], users['user1']['auth_user_id'])
    user_profile_id1a = user_profile_v2(users['user2']['token'],users['user1']['auth_user_id'])
    
    # Ensure the correct output after calling admin_user_remove
    assert f'{user_profile_id1a["user"]["name_first"]} {user_profile_id1a["user"]["name_last"]}' == "Removed user"
    assert messages_channel_id1['messages'][0]['message'] == "Removed user"
    assert messages_channel_id2['messages'][0]['message'] == "Removed user"
    assert messages_dm_id_1['messages'][0]['message'] == "Removed user"

    admin_user_remove_v1(users['user3']['token'], users['user2']['auth_user_id'])
    admin_user_remove_v1(users['user3']['token'], users['user4']['auth_user_id'])


def test_admin_user_remove_testing_functions_errors(setup_user):
    users = setup_user

    # User 1 makes channel 1 
    channel_id1 = channels_create_v2(users['user1']['token'],'Test Channel',True)
    # User 3 joins the public channel
    channel_join_v2(users['user3']['token'], channel_id1['channel_id'])
    # User 1 makes User 3 an owner
    channel_addowner_v1(users['user1']['token'], channel_id1['channel_id'], users['user3']['auth_user_id'])

    # Global User 2 removes Global User 1
    admin_userpermission_change_v1(users['user1']['token'], users['user2']['auth_user_id'], 1)
    admin_userpermission_change_v1(users['user2']['token'], users['user3']['auth_user_id'], 1)   
    # Function called 
    admin_user_remove_v1(users['user2']['token'], users['user1']['auth_user_id'])

    print(channel_details_v2(users['user3']['token'],channel_id1['channel_id']))

    with pytest.raises(InputError):
        channel_invite_v2(users['user3']['token'], channel_id1['channel_id'], users['user1']['auth_user_id'])


def test_admin_user_remove_testing_dm_input_error(setup_user):
    users = setup_user 

    # Function called 
    admin_user_remove_v1(users['user1']['token'], users['user2']['auth_user_id'])

    with pytest.raises(InputError):
        dm_create_v1(users['user3']['token'], [users['user1']['auth_user_id'], users['user2']['auth_user_id']])
    
    dm_id1 = dm_create_v1(users['user1']['token'], [users['user3']['auth_user_id']])

    with pytest.raises(InputError):
        dm_invite_v1(users['user1']['token'], dm_id1['dm_id'], users['user2']['auth_user_id'])


def test_admin_user_remove_testing_admin_input_error(setup_user):
    users = setup_user 

    admin_userpermission_change_v1(users['user1']['token'], users['user2']['auth_user_id'], 1)
    admin_userpermission_change_v1(users['user2']['token'], users['user3']['auth_user_id'], 1)   

    admin_user_remove_v1(users['user1']['token'], users['user2']['auth_user_id'])

    with pytest.raises(InputError):
        admin_user_remove_v1(users['user3']['token'], users['user2']['auth_user_id'])
    
    with pytest.raises(InputError):
        admin_userpermission_change_v1(users['user3']['token'], users['user2']['auth_user_id'], 1)