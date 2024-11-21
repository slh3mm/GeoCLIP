import os
import requests
import json
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim, Photon
from huggingface_hub import HfApi
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.geoguessr.com/api"
DATA_DIR = "data"
IMG_DIR = "images"
COORDS_DIR = f"{DATA_DIR}/coords.csv"
GAMEIDS_DIR = f"{DATA_DIR}/game_ids.txt"
METADATA_DIR = f"{DATA_DIR}/metadata.csv"


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
    response = session.get(f"{BASE_URL}/v3/games/{game_id}")

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

    with open(GAMEIDS_DIR, "r") as id_f:
        with open(COORDS_DIR, "w") as coord_f:
            game_ids = id_f.read().splitlines()
            for game_id in game_ids:
                for lat, lng in retrieve_coords(game_id, session):
                    coord_f.write(f"{lat}, {lng}\n")


def coords_to_metadata():
    data_arr = []
    coords_df = pd.read_csv(COORDS_DIR, header=None, names=["lat", "lng"])
    for i, row in coords_df.iterrows():
        lat, lng = row["lat"], row["lng"]
        response = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?format=geocodejson&lat={lat}&lon={lng}"
        ).json()
        data = response["features"][0]["properties"]["geocoding"]
        data["img_name"] = f"img_{i:05d}.jpg"
        data["lat"] = lat
        data["lng"] = lng
        del data["admin"]
        data_arr.append(data)
        # if i == 20: break
    df = pd.DataFrame(data_arr)

    # Move img_name, lat, lng to front of dataframe
    cols_to_move = ["img_name", "lat", "lng"]
    for i in range(len(cols_to_move)):
        col = df.pop(cols_to_move[i])
        df.insert(i, cols_to_move[i], col)

    df.to_csv(METADATA_DIR, index=False)


def metadata_to_img(metadata_idx):
    gsv_url = "https://maps.googleapis.com/maps/api/streetview?"
    metadata_chunk = pd.read_csv(f"{DATA_DIR}/metadata_{metadata_idx}.csv")
    for i, row in metadata_chunk.iterrows():
        lat, lng = row["lat"], row["lng"]
        pic_params = {
            "key": os.environ["GCP_KEY"],
            "location": f"{lat},{lng}",
            "size": "640x640",
            "heading": "0",
            "pitch": "0",
        }
        img_name = row["img_name"]
        response = requests.get(gsv_url, params=pic_params)
        if response.status_code == 200:
            with open(f"{IMG_DIR}/{img_name}", "wb") as img_f:
                img_f.write(response.content)


def metadata_divide():
    NUM_SPLITS = 4
    metadata = pd.read_csv(METADATA_DIR)
    split_dfs = np.array_split(metadata, NUM_SPLITS)
    for i in range(NUM_SPLITS):
        split_dfs[i].to_csv(f"{DATA_DIR}/metadata_{i}.csv", index=False)


def metadata_to_huggingface():
    api = HfApi()
    api.upload_file(
        path_or_fileobj=METADATA_DIR,
        path_in_repo="metadata.csv",
        repo_id="slh3mm/gsv_images",
        repo_type="dataset",
        token=os.environ["HF_TOKEN"],
    )


def imgs_to_huggingface():
    api = HfApi()
    api.upload_folder(
        folder_path=IMG_DIR,
        repo_id="slh3mm/gsv_images",
        repo_type="dataset",
        token=os.environ["HF_TOKEN"],
    )


def main():
    coords_to_metadata()
    metadata_divide()

    # metadata_to_img(metadata_idx=0)
    # imgs_to_huggingface()
    # metadata_to_huggingface()

    return


if __name__ == "__main__":
    main()
