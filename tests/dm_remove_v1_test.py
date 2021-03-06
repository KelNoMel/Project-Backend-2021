# PROJECT-BACKEND: Team Echo
# Written by Darrell Mounarath

import pytest

from src.error import InputError, AccessError
from src.auth import auth_register_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1
from src.other import clear_v1

# Typical case
def test_function():
    clear_v1()
    a_u_id1 = auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1')
    a_u_id2 = auth_register_v1('example2@hotmail.com', 'password2', 'first_name2', 'last_name2')

    dm_id = dm_create_v1(a_u_id1['token'], [a_u_id2['auth_user_id']])
    
    assert dm_list_v1(a_u_id1['token']) == {
        'dms': [
            {
                'dm_id': dm_id['dm_id'],
                'name': dm_id['dm_name']
            }
        ]
    }

    dm_remove_v1(a_u_id1['token'], dm_id['dm_id'])

    assert dm_list_v1(a_u_id1['token']) == {'dms': []}

# dm_remove removing multiple dms
def test_multiple():
    clear_v1()
    a_u_id1 = auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1')
    a_u_id2 = auth_register_v1('example2@hotmail.com', 'password2', 'first_name2', 'last_name2')
    a_u_id3 = auth_register_v1('example3@hotmail.com', 'password3', 'first_name3', 'last_name3')
    a_u_id4 = auth_register_v1('example4@hotmail.com', 'password4', 'first_name4', 'last_name4')
    a_u_id5 = auth_register_v1('example5@hotmail.com', 'password5', 'first_name5', 'last_name5')

    dm_id2 = dm_create_v1(a_u_id1['token'], [a_u_id2['auth_user_id']])
    dm_id3 = dm_create_v1(a_u_id1['token'], [a_u_id3['auth_user_id']])
    dm_id4 = dm_create_v1(a_u_id1['token'], [a_u_id4['auth_user_id']])
    dm_id5 = dm_create_v1(a_u_id1['token'], [a_u_id5['auth_user_id']])
    
    assert dm_list_v1(a_u_id1['token']) == {
        'dms': [
            {
                'dm_id': dm_id2['dm_id'],
                'name': dm_id2['dm_name']
            },
            {
                'dm_id': dm_id3['dm_id'],
                'name': dm_id3['dm_name']
            },
            {
                'dm_id': dm_id4['dm_id'],
                'name': dm_id4['dm_name']
            },
            {
                'dm_id': dm_id5['dm_id'],
                'name': dm_id5['dm_name']
            }
        ]
    }

    dm_remove_v1(a_u_id1['token'], dm_id2['dm_id'])
    dm_remove_v1(a_u_id1['token'], dm_id3['dm_id'])

    assert dm_list_v1(a_u_id1['token']) == {
        'dms': [
            {
                'dm_id': dm_id4['dm_id'],
                'name': dm_id4['dm_name']
            },
            {
                'dm_id': dm_id5['dm_id'],
                'name': dm_id5['dm_name']
            }
        ]
    }

    dm_remove_v1(a_u_id1['token'], dm_id4['dm_id'])
    dm_remove_v1(a_u_id1['token'], dm_id5['dm_id'])

    assert dm_list_v1(a_u_id1['token']) == {'dms': []}

# dm_remove given invalid token
def test_invalid_token():
    clear_v1()
    a_u_id1 = auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1')
    a_u_id2 = auth_register_v1('example2@hotmail.com', 'password2', 'first_name2', 'last_name2')

    dm_id = dm_create_v1(a_u_id1['token'], [a_u_id2['auth_user_id']])

    with pytest.raises(AccessError):
        dm_remove_v1(12345, dm_id['dm_id'])

# dm_remove given invalid dm_id
def test_invalid_dm_id():
    clear_v1()
    a_u_id1 = auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1')
        
    with pytest.raises(InputError):
        dm_remove_v1(a_u_id1['token'], 12345)

# dm_remove given user who is not the creator of dm
def test_wrong_user():
    clear_v1()
    a_u_id1 = auth_register_v1('example1@hotmail.com', 'password1', 'first_name1', 'last_name1')
    a_u_id2 = auth_register_v1('example2@hotmail.com', 'password2', 'first_name2', 'last_name2')

    dm_id = dm_create_v1(a_u_id1['token'], [a_u_id2['auth_user_id']])
    
    with pytest.raises(AccessError):
        dm_remove_v1(a_u_id2['token'], dm_id['dm_id'])

