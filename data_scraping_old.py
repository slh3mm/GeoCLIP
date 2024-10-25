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

with SB(uc=True, test=True) as sb:
    url = "https://www.geoguessr.com/signin"
    sb.uc_open_with_reconnect(url)
    # sb.open(url)
    # sb.assert_element('[name="email"]')
    sb.driver.type('[name="email"]', os.environ["UNAME"])
    sb.type('[name="password"]', os.environ["PWORD"])
    sb.uc_gui_click_captcha()
    sb.driver.uc_click('[data-qa="login-cta-button"]')

    # Initialize Chrome Session, create wait object, go to geoguessr.com
    # driver = webdriver.Chrome()
    # wait = WebDriverWait(driver, 10)
    # driver.get("https://www.geoguessr.com/signin")

    # Wait for elements to load
    # email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
    # password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    # login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-qa="login-cta-button"]')))

    # # Enter username and password, click login
    # email_input.send_keys(os.environ["UNAME"])
    # password_input.send_keys(os.environ["PWORD"])
    # login_button.click()

# Redirect to game page, press play
# driver.get("https://www.geoguessr.com/maps/world/play")
# play_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-qa="start-game-button"]')))
# play_button.click()

# # Wait for game to load
# wait.until(EC.url_contains("/game/"))

# # Play N_GAMES games, each with 5 rounds
# N_GAMES = 2
# SAVE_RATE = 20
# game_id_buffer = ""
# for game in range(N_GAMES):
#     # Grab game url and game id
#     game_url = driver.current_url
#     game_id = game_url.split("/")[-1]
#     game_id_buffer += game_id + "\n"
#     print(game_id)
    
#     # Save game_id every SAVE_RATE games
#     if game % SAVE_RATE == 0:
#         with open("game_ids.txt", "a") as f:
#             f.write(f"{game_id_buffer}\n")
#             f.close()
#         game_id_buffer = ""
        
#     # Play the 5 rounds of a game
#     for round in range(5):
#         guess_map_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-qa="guess-map"]')))
#         guess_map_element.click()

#         guess_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-qa="perform-guess"]')))
#         guess_button.click()

#         next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-qa="close-round-result"]')))
#         next_button.click()
            
#     # Start new game
#     play_again_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-qa="play-again-button"]')))
#     play_again_button.click()
    
#     # Wait for new game to load
#     wait.until(lambda driver: driver.current_url != game_url)
    
# driver.quit()