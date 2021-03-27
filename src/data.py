from src.other import clear_v1
#from other import clear_v1


# Iteration 1 test data
data = {
    'users' : {
        35746842521 : {
            'name_first' : 'first_name1',
            'name_last' : 'last_name1',
            'email' : 'example1@hotmail.com',
            'password' : 'password1',
            'handle_str' : 'first_name1last_name',
            'permission_id': 1,
            'notifications' : [
                {
                    'channel_id' : 14723573315,
                    'dm_id' : -1,
                    'notification_message' : 'first_name2last_name added you to channel1',
                },
                {
                    'channel_id' : -1,
                    'dm_id' : 4561328123,
                    'notification_message' : 'first_name2last_name reacted to your message in channel1',
                },
            ]
        },
        11753764853 : {
            'name_first' : 'first_name2',
            'name_last' : 'last_name2',
            'email' : 'example2@hotmail.com',
            'password' : 'password2',
            'handle_str' : 'first_name2last_name',
            'permission_id': 2,
            'notifications' : [
                {
                    'channel_id' : 14723573315,
                    'dm_id' : -1,
                    'notification_message' : 'first_name1last_name added you to channel1',
                },
                {
                    'channel_id' : -1,
                    'dm_id' : 4561328124,
                    'notification_message' : 'first_name1last_name reacted to your message in channel1',
                },
            ]
        },
    },
    'channels' : {
        14723573315 : {
            'name' : 'channel1',
            'is_public' : True,
            'owner_members' : ['auth_user_id1'],
            'all_members' : ['auth_user_id1', 'auth_user_id2'],
            'messages' : [
                {
                    'message_id': 4561328123,
                    'u_id': 35746842521,
                    'message': 'Hello World1',
                    'time_created': 123416589,
                },
                {
                    'message_id': 61510648893,
                    'u_id': 11753764853,
                    'message': 'Hello World2',
                    'time_created': 123456789,
                },
            ]
        },
        31627643273 : {
            'name' : 'channel2',
            'is_public' : True,
            'owner_members' : [123456789],
            'all_members' : [123456789, 12389473129847],
            'messages' : [
                {
                    'message_id': 12354122383,
                    'u_id': 35746842521,
                    'message': 'Hello World1',
                    'time_created': 45132806512,
                },
                {
                    'message_id': 123156231064,
                    'u_id': 11753764853,
                    'message': 'Hello World2',
                    'time_created': 68741450315603,
                }
            ],
        },
    },
    'dms': {
        1691360831: {
            'name': 'dms1',
            'members': [35746842521, 11753764853],
            'messages' : [
                {
                    'message_id': 12354122383,
                    'u_id': 35746842521,
                    'message': 'Hello World1',
                    'time_created': 45132806512,
                },
                {
                    'message_id': 123156231064,
                    'u_id': 11753764853,
                    'message': 'Hello World2',
                    'time_created': 68741450315603,
                },
            ],
        }
    },
    'messages' : [
        {
            'message_id': 4650166837,
            'u_id': 46541861546,
            'message': "Random message",
            'time_created': 753159468,
            'channel_id': 416514684,
            'dm_id': -1,
            'is_removed': False,
            'was_shared': False,
        },
        {
            'message_id': 789416137,
            'u_id': 1234567846,
            'message': "Random message",
            'time_created': 521159468,
            'channel_id': -1,
            'dm_id': 1691360831,
            'is_removed': False,
            'was_shared': False,
        },
    ],
}


# Function to reset the data to default (assists in testing)
def reset_data():
    global data
    data = clear_v1()
    return data

def retrieve_data():
    global data
    return data
