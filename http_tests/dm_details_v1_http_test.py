# PROJECT-BACKEND: Team Echo
# Written by Darrell Mounarath

import json
import requests
import urllib

from src.config import url

###                         HELPER FUNCTIONS                           ###

def user_body(num):
    return {
        "email": f"example{num}@hotmail.com",
        "password": f"password{num}",
        "name_first": f"first_name{num}",
        "name_last": f"last_name{num}"
    }

def dm_create_body(user, u_ids): 
    u_ids_list = [u_id['auth_user_id'] for u_id in u_ids]
    return {
        "token": user["token"],
        "u_ids": u_ids_list
    }

def dm_details_body(user, dm):
    return {
        "token": user["token"],
        "dm_id": dm["dm_id"]
    }

###                       END HELPER FUNCTIONS                         ###

def test_invalid_dm_id():
    requests.delete(f"{url}clear/v1")
    
    a_u_id0 = requests.post(f"{url}auth/register/v2", json=user_body(0))
    user0 = a_u_id0.json()

    payload = requests.get(f"{url}dm/details/v1", params=dm_details_body(user0, {"dm_id": 5031705713}))
    dm_details = payload.json()

    assert dm_details["code"] == 400
    assert dm_details["name"] == "System Error"
    assert dm_details["message"] == "<p></p>"

def test_invalid_user():
    requests.delete(f"{url}clear/v1")
    
    users = []
    for i in range(3):
        a_u_id = requests.post(f"{url}auth/register/v2", json=user_body(i))
        users.append(a_u_id.json())

    dm_id0 = requests.post(f"{url}dm/create/v1", json=dm_create_body(users[0], [users[1]]))
    dm0 = dm_id0.json()

    payload = requests.get(f"{url}dm/details/v1", params=dm_details_body(users[2], dm0))
    dm_details = payload.json()

    assert dm_details["code"] == 403
    assert dm_details["name"] == "System Error"
    assert dm_details["message"] == "<p></p>"

def test_invalid_token():
    requests.delete(f"{url}clear/v1")
    
    a_u_id0 = requests.post(f"{url}auth/register/v2", json=user_body(0))
    user0 = a_u_id0.json()

    a_u_id1 = requests.post(f"{url}auth/register/v2", json=user_body(1))
    user1 = a_u_id1.json()

    dm_id0 = requests.post(f"{url}dm/create/v1", json=dm_create_body(user0, [user1]))
    dm0 = dm_id0.json()

    payload = requests.get(f"{url}dm/details/v1", params=dm_details_body({"token": 501730570}, dm0))
    dm_details = payload.json()

    assert dm_details["code"] == 403
    assert dm_details["name"] == "System Error"
    assert dm_details["message"] == "<p></p>"
