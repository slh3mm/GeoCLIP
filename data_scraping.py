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

# Uses api endpoint to retrieve lat, lng of a game
def api_retrieve_coords(game_id, session):
    # Existing game_id
    game_id = "gAiSgeQDjv8uT9ZL"
    response = session.get(f"https://www.geoguessr.com/api/v3/games/{game_id}")

    # If 200 OK, parse JSON and return lat, lng
    if response.status_code == 200:
        data = json.loads(response.text)
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

# Initialize Chrome Session, go to geoguessr.com\
driver = webdriver.Chrome()
driver.get("https://www.geoguessr.com/signin")

# Wait for elements to load
time.sleep(4)
email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))

# Enter username and password, click login
time.sleep(random.uniform(2,3))
email_input.send_keys(os.environ["UNAME"])
time.sleep(random.uniform(2,3))
password_input.send_keys(os.environ["PWORD"])
time.sleep(random.uniform(2,3))
login_button.click()
time.sleep(random.uniform(2, 3))

# Redirect to game page, press play
driver.get("https://www.geoguessr.com/maps/world/play")
play_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-qa="start-game-button"]')))
time.sleep(random.uniform(2,3))
play_button.click()

# Wait for game to load, retrieve game_id from url
game_url = driver.current_url
game_id = game_url.split("/")[-1]
print(game_id)

time.sleep(30)

# Exit safely
driver.quit()