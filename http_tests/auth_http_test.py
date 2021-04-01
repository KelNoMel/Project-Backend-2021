from src.error import InputError
import requests
import time
import pytest 
from src import config
import json
from src.auth import blacklist, auth_decode_token, auth_token_ok, auth_decode_token

@pytest.fixture(autouse=True)
def reset():
	requests.delete(config.url + 'clear/v1', params={})

# client and app are pytest fixtures
def test_auth_register_api_valid():
	resp = requests.post(config.url + 'auth/register/v2', params={'email':'exampleUserEmail@email.com', 'password':'ExamplePassword', 'name_first':'FIRSTNAME', 'name_last':'LASTNAME'})
	json_data = json.loads(resp.text)

	assert json_data['token'] and json_data['token'] != ''
	assert json_data['auth_user_id'] and json_data['auth_user_id'] != 1


# testing the exception handler, for this password is too short 
def test_auth_register_api_invalid_exception():
	resp = requests.post(config.url + 'auth/register/v2', params={'email' : 'exampleUserEmail@email.com', 'password':'123', 'first_name':'FIRSTNAME', 'last_name':'LASTNAME'})
	json_data = json.loads(resp.text)

	assert json_data['name']
	assert json_data['code']
	assert json_data['message']	# just '<p></p>'


def test_auth_login_api_valid():
	# register first 
	resp = requests.post(config.url + 'auth/register/v2', params={'email':'exampleUserEmail@email.com', 'password':'ExamplePassword', 'name_first':'FIRSTNAME', 'name_last':'LASTNAME'})
	json_data_register = json.loads(resp.text)

	resp_login = requests.post(config.url + 'auth/login/v2', params={'email':'exampleUserEmail@email.com', 'password':'ExamplePassword'})
	json_data_login = json.loads(resp_login.text)

	assert json_data_login['token']
	assert json_data_login['auth_user_id'] == json_data_register['auth_user_id']


def test_auth_login_api_invalid():
	# register 
	response_register = requests.post(config.url + 'auth/register/v2', params={'email':'exampleUserEmail@email.com', 'password':'ExamplePassword', 'name_first':'FIRSTNAME', 'name_last':'LASTNAME'})
	json_data_register = json.loads(response_register.text)
	assert json_data_register['token']

	# if credentials don't match, handled by customized exception handler 
	response_login = requests.post(config.url + 'auth/login/v2', params={'email':'exampleUserEmail@email.com', 'password':'wrongpassword'})
	json_data_login = json.loads(response_login.text)

	assert json_data_login['code'] == 400 # this is just status_code
	assert json_data_login['name'] == 'System Error'
	assert json_data_login['message']


def test_auth_logout_api():
	# register
	response_register = requests.post(config.url + 'auth/register/v2', params={'email':'exampleUserEmail@email.com', 'password':'ExamplePassword', 'name_first':'FIRSTNAME', 'name_last':'LASTNAME'})
	json_data_register = json.loads(response_register.text)
	token_kept_by_client = json_data_register['token']

	# logout
	response_logout1 = requests.post(config.url + 'auth/logout/v1', params={'token':token_kept_by_client})
	json_data_logout1 = json.loads(response_logout1.text)
	assert json_data_logout1['is_success'] == True

	# logout again with the same token, blacklisted since we've already logged out
	response_logout2 = requests.post(config.url + 'auth/logout/v1', params={'token':token_kept_by_client})
	json_data_logout2 = json.loads(response_logout2.text)
	assert json_data_logout2['is_success'] == False


def test_auth_logout_api_logging_back():
	# register
	response_register = requests.post(config.url + 'auth/register/v2', params={'email':'exampleUserEmail@email.com', 'password':'ExamplePassword', 'name_first':'FIRSTNAME', 'name_last':'LASTNAME'})
	json_data_register = json.loads(response_register.text)
	token_kept_by_client = json_data_register['token']
	auth_user_id = auth_decode_token(token_kept_by_client)

	# logout
	response_logout = requests.post(config.url + 'auth/logout/v1', params={'token':token_kept_by_client})
	json_data_logout = json.loads(response_logout.text)
	assert json_data_logout['is_success'] == True

	# log back in
	response_login = requests.post(config.url + 'auth/login/v2', params={'email':'exampleUserEmail@email.com', 'password':'ExamplePassword'})
	json_data_login = json.loads(response_login.text)
	assert json_data_login['token']

	# assert the user is no longer in the blacklist and token is valid again
	assert auth_user_id not in blacklist
	assert auth_token_ok(token_kept_by_client) == True
