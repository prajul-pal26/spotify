import base64
from dotenv import load_dotenv
import os
import requests
from requests import get, post 
import json


def get_token():
    client_id = '59a919435d414df88f288b5a7bcc45c6'
    client_secret = '100bd40eed1143399e55a3ed9d639c00'

    # Encode client ID and client secret in base64
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    # Spotify token endpoint URL
    token_url = 'https://accounts.spotify.com/api/token'

    # Data for the POST request
    token_data = {
        'grant_type': 'client_credentials'
    }

    # Headers for the POST request
    token_headers = {
        'Authorization': f'Basic {client_creds_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make the POST request to get the token
    response = requests.post(token_url, data=token_data, headers=token_headers)

    # Check if the request was successful
    if response.status_code == 200:
        token_response_data = response.json()
        access_token = token_response_data['access_token']
        return access_token



def get_auth_header(token):
    return {"Authorization":"Bearer "+token}

def search_for_artist(artist_name):
    url="https://api.spotify.com/v1/search"
    headers=get_auth_header(get_token())   
    query=f"?q={artist_name}&type=artist&limit=1"
    
    query_url=url+query
    result=get(query_url,headers=headers)
    json_result=json.loads(result.content)
    return json_result
    
search_for_artist("Arijit Singh")
    
def top_artists():
    
    url=f"https://api.spotify.com/v1/browse/categories/toplists/playlists"

    headers=get_auth_header(get_token())
    result=get(url,headers=headers)
    json_result=json.loads(result.content)
    return json_result
top_artists()
    
    
def top_trek():
    
    url=f"https://api.spotify.com/v1/browse/categories/toplists/playlists"

    headers=get_auth_header(get_token())
    result=get(url,headers=headers)
    json_result=json.loads(result.content)
    return json_result
top_trek()
    
def track():
    url=f"https://api.spotify.com/v1/playlists/0cJXodCZCl2EWRNcw6m1eJ"
    


    headers=get_auth_header(get_token())

    result=get(url,headers=headers)
    if result.status_code==200:
        json_result=json.loads(result.content)
        return json_result

    
track()
    
def get_popular_playlists():
    url = f"https://api.spotify.com/v1/playlists/37i9dQZF1DXdpQPPZq3F7n/tracks?limit=1"
    headers = get_auth_header(get_token())
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        playlists = response.json()
        return playlists
    else:
        print(f"Failed to get popular playlists: {response.status_code}, {response.text}")
        return None


def get_artist_by_id():
    url="https://api.spotify.com/v1/search?q=ArijitSingh&type=artist&limit=1"
    headers = get_auth_header(get_token())
    
    response = requests.get(url, headers=headers)
    data=response.json()
    id=data["artists"]['items'][0]['id'] 
    songs_url=f"https://api.spotify.com/v1/artists/{id}/top-tracks?market=IN"
    headers2 = get_auth_header(get_token())
    
    response = requests.get(songs_url, headers=headers2)
    data2=response.json()
    # for track in data2['tracks']:
        
print(get_artist_by_id())