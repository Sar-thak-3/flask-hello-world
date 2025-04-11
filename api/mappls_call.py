import requests

def search_place(query, location=None, token_type='Bearer', access_token=''):
    headers = {
        'Authorization': f'{token_type} {access_token}'
    }

    base_url = 'https://atlas.mapmyindia.com/api/places/textsearch/json'
    params = {
        'query': query,
        'region': 'IND'
    }

    if location:
        params['location'] = location

    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# 🧪 Example usage:
# if __name__ == '__main__':
#     details_got = {
#         "access_token":"80b4a185-6c40-4342-8c24-1a3014f0ff8c",
#         "token_type":"bearer",
#         "expires_in":86399,
#         "scope":"READ",
#         "project_code":"prj1744354767i2078286208",
#         "client_id":"96dHZVzsAut6JhXpKxI9nWuPQcbDvYIxnBL7JfjOqFC3B4-oCzvE9ym_AFe9NUQ4f_-VHiOejfZf9HiWzYCNqw=="
#     }
#     access_token = details_got['access_token']
#     token_type = 'Bearer'  # Or whatever token_type you received
#     query = 'cafes'
#     location = '12.980000,80.040000'  # Latitude,Longitude

#     result = search_place(query=query, location=location, token_type=token_type, access_token=access_token)
#     print(result)