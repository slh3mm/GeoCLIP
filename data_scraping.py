import time
import requests
import os
import json
import random
from dotenv import load_dotenv; load_dotenv();
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Uses api endpoint to retrieve lat, lng of a game
def api_retrieve_coords(game_id, session):
    # Existing game_id
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
    
# Create session, set cookies using retrieved NCFA from login at https://geoguessr.com
session = requests.Session()
ncfa = os.environ["NCFA"]
session.cookies.set("_ncfa", ncfa, domain="www.geoguessr.com")

# Initialize Chrome Session, create wait object, go to geoguessr.com
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
driver.get("https://www.geoguessr.com/signin")

# Wait for elements to load
email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))

# Enter username and password, click login
email_input.send_keys(os.environ["UNAME"])
password_input.send_keys(os.environ["PWORD"])
login_button.click()

# Redirect to game page, press play
wait.until(EC.url_to_be("https://www.geoguessr.com/"))
driver.get("https://www.geoguessr.com/maps/world/play")
play_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-qa="start-game-button"]')))
play_button.click()

# Wait for game to load
wait.until(EC.url_contains("/game/"))

# Play N_GAMES games, each with 5 rounds
N_GAMES = 2
SAVE_RATE = 20
game_id_buffer = ""
for game in range(N_GAMES):
    # Grab game url and game id
    game_url = driver.current_url
    game_id = game_url.split("/")[-1]
    game_id_buffer += game_id + "\n"
    print(game_id)
    
    # Save game_id every SAVE_RATE games
    if game % SAVE_RATE == 0:
        with open("game_ids.txt", "a") as f:
            f.write(f"{game_id_buffer}\n")
            f.close()
        game_id_buffer = ""
        
    # Play the 5 rounds of a game
    for round in range(5):
        guess_map_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-qa="guess-map"]')))
        guess_map_element.click()

        guess_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-qa="perform-guess"]')))
        guess_button.click()

        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-qa="close-round-result"]')))
        next_button.click()
            
    # Start new game
    play_again_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-qa="play-again-button"]')))
    play_again_button.click()
    
    # Wait for new game to load
    wait.until(lambda driver: driver.current_url != game_url)

# Exit safely
driver.quit()