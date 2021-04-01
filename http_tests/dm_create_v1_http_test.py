import json
import requests
import urllib

from src.data import retrieve_data

# HELPER FUNCTIONS

def user_body(num):
    return {
        "email": f"example{num}@hotmail.com",
        "password": f"password{num}",
        "name_first": f"first_name{num}",
        "name_last": f"last_name{num}"
    }

def dm_create_body(user, u_ids): 
    u_ids_list = [u_id['auth_user_id'] for u_id in uids]
    return {
        "token": user["token"],
        "u_ids": u_ids_list
    }

BASE_URL = 'http://127.0.0.1:6000'

def test_function():
    requests.delete(f"{BASE_URL}/clear/v1")
    
    a_u_id0 = requests.post(f"{BASE_URL}/auth/register/v2", json=user_body(0))
    user0 = a_u_id0.json()

    a_u_id1 = requests.post(f"{BASE_URL}/auth/register/v2", json=user_body(1))
    user1 = a_u_id1.json()

    dm_id0 = requests.post(f"{BASE_URL}/dm/create/v1", json=dm_create_body(user0, [user1]))
    dm0 = dm_id0.json()

    assert dm0 == {
        'dm_id': data['users'][a_u_id1['auth_user_id']]['dms'][0],
        'dm_name': 'first_name1last_name, first_name2last_name'
    }