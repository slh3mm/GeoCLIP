import os
import requests
import json

# Not sure if this function is needed
# Uses api endpoint to log into geoguessr
def api_login(session):
    # Construct Payload using username and password for geoguessr
    login_url = "https://www.geoguessr.com/api/v3/accounts/signin/"
    username = os.environ["UNAME"]
    password = os.environ["PWORD"]
    payload = {
        "email": username,
        "password": password,
        "remember": True
    }
    
    # Send POST request, return response
    response = session.post(login_url, json=payload)
    if response.status_code == 200:
        print("Login successful")
    else:
        print(f"Error: {response.status_code}")
        
# Uses api endpoint to retrieve lat, lng of a game
def api_retrieve_coords(game_id, session):
    # Existing game_id(s) for testing
    game_id = "gAiSgeQDjv8uT9ZL"
    game_id = "nlcIiBl9ebYC8BXh"
    response = session.get(f"https://www.geoguessr.com/api/v3/games/{game_id}")

    # If 200 OK, parse JSON and return lat, lng
    if response.status_code == 200:
        data = json.loads(response.text)
        print(data)
        lat = data['rounds'][0]['lat']
        lng = data['rounds'][0]['lng']
        return lat, lng
    else:
        print(f"Error: {response.status_code}")
    
# Create session, set cookies using retrieved NCFA from login at https://geoguessr.com
session = requests.Session()
ncfa = os.environ["NCFA"]
session.cookies.set("_ncfa", ncfa, domain="www.geoguessr.com")

# Iterate through game_ids.txt, retrieve lat, lng of each game
with open("game_ids.txt", "r") as f:
    game_ids = f.read().splitlines()
    for game_id in game_ids:
        lat, lng = api_retrieve_coords(game_id, session)
        print(f"Lat: {lat}, Lng: {lng}")
    f.close()