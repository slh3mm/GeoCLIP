import os
import requests
import json
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim, Photon
from datasets import load_dataset
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
def id_to_coords():
    # Create session, set cookies using retrieved NCFA from login at https://geoguessr.com
    session = requests.Session()
    session.cookies.set("_ncfa", os.environ["NCFA"], domain="www.geoguessr.com")
    
    with open("src/scraping/game_ids.txt", "r") as id_f:
        with open("src/scraping/coords.csv", "w") as coord_f:
            game_ids = id_f.read().splitlines()
            for game_id in game_ids:
                for lat, lng in retrieve_coords(game_id, session):
                    coord_f.write(f"{lat}, {lng}\n")
            coord_f.close()
        id_f.close()


def coords_to_metadata():
    data_arr = []
    coords_df = pd.read_csv("src/scraping/coords.csv", header=None, names=["lat", "lng"])
    for i, row in coords_df.iterrows():
        lat, lng = row["lat"], row["lng"]
        response = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=geocodejson&lat={lat}&lon={lng}").json()
        data = response["features"][0]["properties"]["geocoding"]
        data["img_name"] = f"img_{i:05d}.jpg"
        data["lat"] = lat
        data["lng"] = lng
        del data["admin"]
        data_arr.append(data)
    df = pd.DataFrame(data_arr)
    
    # Move img_name, lat, lng to front of dataframe
    cols_to_move = ["img_name", "lat", "lng"]
    for i in range(len(cols_to_move)):
        col = df.pop(cols_to_move[i])
        df.insert(i, cols_to_move[i], col)
        
    df.to_csv("src/scraping/metadata.csv", index=False)

def coords_to_img():
    # TODO: retrieve image from google api
    #img = 
    
    pass

def metadata_divide(num_splits):
    metadata = pd.read_csv("src/scraping/metadata.csv")
    split_dfs = np.array_split(metadata, num_splits)
    for i in range(num_splits):
        split_dfs[i].to_csv(f"src/scraping/metadata_{i}.csv", index=False)

def metadata_train_test_split(train_frac):
    metadata = pd.read_csv("src/scraping/metadata.csv")
    train_df = metadata.sample(frac=train_frac)
    test_df = metadata.drop(train_df.index)
    train_df.to_csv("images/train/metadata.csv", index=False)
    test_df.to_csv("images/test/metadata.csv", index=False)
    
def main():
    # Use geopy to convert lat, lng to country
    coords_to_metadata()
    metadata_divide(4)
    return


if __name__ == "__main__":
    main()
