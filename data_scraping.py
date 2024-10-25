import undetected_chromedriver as uc
import os
import time
from dotenv import load_dotenv; load_dotenv();
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
from seleniumbase import SB
from seleniumbase import Driver

# Initialize Chrome Session
with SB(uc=True, test=True) as sb:
    # Go to geoguessr.com, enter login info, bypass captcha, click login
    sb.uc_open_with_reconnect("https://www.geoguessr.com/signin")
    sb.type('[name="email"]', os.environ["UNAME"])
    sb.type('[name="password"]', os.environ["PWORD"])
    sb.uc_gui_click_captcha()
    sb.click('[data-qa="login-cta-button"]')

    # Redirect to game page, press play
    sb.driver.get("https://www.geoguessr.com/maps/world/play")
    sb.uc_click('[data-qa="start-game-button"]')

    # Play N_GAMES games, each with 5 rounds
    N_GAMES = 2
    SAVE_RATE = 1
    game_id_buffer = ""
    for game in range(N_GAMES):
        # Grab game url and game id
        game_url = sb.get_current_url()
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
            sb.click('[data-qa="guess-map"]')
            sb.click('[data-qa="perform-guess"]')
            sb.click('[data-qa="close-round-result"]')
                
        # Start new game
        sb.click('[data-qa="play-again-button"]')