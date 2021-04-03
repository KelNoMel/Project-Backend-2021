import pytest

from src.error import InputError
from src.auth import auth_login_v1, auth_email_format, auth_register_v1, auth_encode_token, auth_decode_token, auth_token_ok, auth_logout_v1, blacklist
from src.data import reset_data, retrieve_data
import time

from src.other import clear_v1
import json

#from error import InputError
#from auth import auth_login_v1, auth_email_format, auth_register_v1
#from data import clear_v1, retrieve_data

@pytest.fixture
def test_users():
    clear_v1()

    dict1 = auth_register_v1('user1@email.com', 'User1_pass!', 'user1_first', 'user1_last')
    dict2 = auth_register_v1('user2@email.com', 'User2_pass!', 'user2_first', 'user2_last')
    dict3 = auth_register_v1('user3@email.com', 'User3_pass!', 'user3_first', 'user3_last')
    dict4 = auth_register_v1('user4@email.com', 'User4_pass!', 'user4_first', 'user4_last')
    dict5 = auth_register_v1('user5@email.com', 'User5_pass!', 'user5_first', 'user5_last')

    return {
        'login1' : dict1,
        'login2' : dict2,
        'login3' : dict3,
        'login4' : dict4,
        'login5' : dict5
    }


def test_auth_email_format():
    assert auth_email_format('123@gmailcom') == False, 'invalid email format'
    assert auth_email_format('jsfdsfdsds123.con') == False, 'invalid email format'
    assert auth_email_format('myvalidemail@yahoogmail.com') == True, 'valid email format'


def test_auth_login_v1(test_users):
    loginResponse = auth_login_v1('user1@email.com', 'User1_pass!')
    assert loginResponse['auth_user_id'] == f"{test_users['login1']['auth_user_id']}"

    with pytest.raises(InputError):
        auth_login_v1('nonexistentKey@gmail.com', 'notimportantpasswd') # can't find a match
    with pytest.raises(InputError):
        auth_login_v1('jsfdsfdsds123.con', '123456') # invalid email format 


def test_auth_register_v1():
<<<<<<< HEAD
    clear_v1()

=======
    data = reset_data()
    
>>>>>>> userprofile-v2
    registerDict = auth_register_v1('example1@hotmail.com', 'password1', 'bob', 'builder')
    with open("data.json", "r") as FILE:
        data = json.load(FILE)
    assert data['users'][f"{registerDict['auth_user_id']}"]['handle_str'] == 'bobbuilder'

    with pytest.raises(InputError):
        auth_register_v1('example1@hotmail.com', 'password1', 'test', 'user1') # duplicate key(email)
    with pytest.raises(InputError):
        auth_register_v1('sampleemail1gmail.com', 'password1', 'test', 'user1') # invalid email format 
    with pytest.raises(InputError):
        auth_register_v1('sampleemail2@gmail.com', '12345', 'test', 'user1') # password too short, less than 6 chars
    with pytest.raises(InputError):
        auth_register_v1('sampleemail3@gmail.com', 'passwo', '', 'user1') # invalid firstname length 

def test_auth_register_v1_nonunique_handle():
    clear_v1()
    
    r1 = auth_register_v1('example1@hotmail.com', 'password1', 'bob', 'builder')
    r2 = auth_register_v1('example2@hotmail.com', 'password1', 'bob', 'builder')

    with open("data.json", "r") as FILE:
        data = json.load(FILE)

    print(data['users'])
    assert data['users'][f"{r1['auth_user_id']}"]['handle_str'] == 'bobbuilder'
    assert data['users'][f"{r2['auth_user_id']}"]['handle_str'] == 'bobbuilder0'

def test_check_auth_permissions(test_users):
    with open("data.json", "r") as FILE:
        data = json.load(FILE)

    assert data['users'][f"{test_users['login1']['auth_user_id']}"]['permission_id'] == 1 # admin
    assert data['users'][f"{test_users['login2']['auth_user_id']}"]['permission_id'] == 2 # non-admin
    assert data['users'][f"{test_users['login3']['auth_user_id']}"]['permission_id'] == 2 # etc
    assert data['users'][f"{test_users['login4']['auth_user_id']}"]['permission_id'] == 2
    assert data['users'][f"{test_users['login5']['auth_user_id']}"]['permission_id'] == 2

def test_encode_decode_token(test_users):
    token = auth_encode_token(test_users['login1']['auth_user_id'])
    assert isinstance(token, str) == True
    assert auth_decode_token(token) == test_users['login1']['auth_user_id']
    assert auth_decode_token('whatisthis') == 'invalid token, log in again'

    time.sleep(6)
    assert auth_decode_token(token) == 'Session expired, log in again'


def test_auth_token_ok():
    token = auth_encode_token(123)
    assert auth_token_ok(token) == True
    bad_token = 'edaeddawedead'
    assert auth_token_ok(bad_token) == False


def test_auth_logout(test_users):
    # logout
    resp_logout1 = auth_logout_v1(test_users['login1']['token'])
    assert resp_logout1 == {'is_success' : True}

    # logout again with the same token, blacklisted since we've already logged out
    resp_logout2 = auth_logout_v1(test_users['login1']['token'])
    assert resp_logout2 == {'is_success' : False}


def test_auth_logout_logging_back(test_users):
    # logout
    resp_logout = auth_logout_v1(test_users['login1']['token'])
    assert resp_logout == {'is_success' : True}
    assert test_users['login1']['auth_user_id'] in blacklist

    # log back in
    resp_login = auth_login_v1('user1@email.com', 'User1_pass!')
    assert resp_login['auth_user_id'] == test_users['login1']['auth_user_id']
    assert resp_login['token']

    # assert the user is no longer in the blacklist and token is valid again
    assert resp_login['auth_user_id'] not in blacklist
    assert auth_token_ok(resp_login['token']) == True

