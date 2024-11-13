import os
import requests
import json
from geopy.geocoders import Nominatim, Photon
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.geoguessr.com/api"


# Not sure if this function is needed
# Uses api endpoint to log into geoguessr
def login(session):
    # Construct Payload using username and password for geoguessr
    login_url = f"{BASE_URL}/v3/accounts/signin/"
    payload = {"email": os.environ["UNAME"], "password": os.environ["PWORD"]}

    # Send POST request, return response
    response = session.post(login_url, json=json.dumps(payload))
    try:
        if response.status_code == 200:
            print("Login successful")
        else:
            print(f"Error {response.status_code}")
    except Exception as e:
        raise e


# Not sure if this function is needed either
# Use api endpoint to log out of geoguessr
def logout(session):
    logout_url = f"{BASE_URL}/v3/accounts/signout/"
    response = session.post(logout_url)
    try:
        if response.status_code == 200:
            print("Logout successful")
        else:
            print(f"Error {response.status_code}")
    except Exception as e:
        raise e


# Uses api endpoint to retrieve lat, lng of a game
def retrieve_coords(game_id, session):
    # Existing game_id(s) for testing
    # game_id = "gAiSgeQDjv8uT9ZL"
    # game_id = "nlcIiBl9ebYC8BXh"
    # game_id = "rYsAcVqH2alGCMXn"
    response = session.get(f"https://www.geoguessr.com/api/v3/games/{game_id}")

    # If 200 OK, parse JSON and return lat, lng
    try:
        if response.status_code == 200:
            data = json.loads(response.text)
            coords = [(round["lat"], round["lng"]) for round in data["rounds"]]
            return coords

        print(f"Error {response.status_code}")
    except Exception as e:
        raise e


# Open game id file and coords file, iterate through game_ids.txt, retrieve lat, lng of each game, write to coords.txt
def id_to_coords(session):
    with open("src/scraping/game_ids.txt", "r") as id_f:
        with open("src/scraping/coords.txt", "w") as coord_f:
            game_ids = id_f.read().splitlines()
            for game_id in game_ids:
                for lat, lng in retrieve_coords(game_id, session):
                    coord_f.write(f"{lat}, {lng}\n")
            coord_f.close()
        id_f.close()


def coords_to_country():
    geolocator = Photon(user_agent="geoapiExercises")
    with open("src/scraping/coords.txt", "r") as coord_f:
        coords = coord_f.read().splitlines()
        for coord in coords:
            lat, lng = coord.split(", ")
            location = geolocator.reverse(f"{lat}, {lng}").raw["properties"]
            metadata = (
                location["country"],
                location["city"],
                location["postcode"],
                location["locality"],
                location["county"],
                location["type"],
                location["osm_key"],
                location["district"],
                location["osm_value"],
                location["name"],
                location["state"],
            )
            # TODO: retrieve image from google api
            #img = 
        coord_f.close()


def main():
    # Create session, set cookies using retrieved NCFA from login at https://geoguessr.com
    # session = requests.Session()
    # session.cookies.set("_ncfa", os.environ["NCFA"], domain="www.geoguessr.com")
    # id_to_coords(session)

    # Use geopy to convert lat, lng to country
    coords_to_country()


if __name__ == "__main__":
    main()
