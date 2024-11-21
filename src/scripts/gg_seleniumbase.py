import os
import time
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from seleniumbase import SB
from selenium.webdriver.common.action_chains import ActionChains

load_dotenv()


# Initialize Chrome Session
with SB(uc=True, incognito=True, locale_code="en") as sb:
    # Go to geoguessr.com, enter login info, bypass captcha, click login
    sb.driver.uc_open_with_reconnect("https://www.geoguessr.com/signin")
    sb.driver.uc_gui_click_captcha()

    # Enter login info automatically
    sb.type('[data-qa="email-field"]', os.environ["UNAME"])
    sb.type('[data-qa="password-field"]', os.environ["PWORD"])
    sb.uc_click('[data-qa="login-cta-button"]', reconnect_time=4)

    # Start game
    sb.driver.get("https://www.geoguessr.com/maps/world/play")
    sb.driver.click('[data-qa="start-game-button"]')

    # Play N_GAMES games, each with 5 rounds
    N_GAMES = 5000
    SAVE_RATE = 5
    game_id_buffer = ""
    for game in range(N_GAMES):
        # Grab game url and game id
        game_url = sb.get_current_url()
        game_id = game_url.split("/")[-1]
        if game_id != "audio.html":
            game_id_buffer += game_id + "\n"

        # Save game_id every SAVE_RATE games
        if game % SAVE_RATE == 0:
            with open("game_ids.txt", "a") as f:
                f.write(f"{game_id_buffer}")
                f.close()
            game_id_buffer = ""

        # Play the 5 rounds of a game
        for round in range(5):
            sb.click('[data-qa="guess-map"]')
            sb.click('[data-qa="perform-guess"]')
            sb.click('[data-qa="close-round-result"]')

        # Start new game
        sb.click('[data-qa="play-again-button"]')
        sb.sleep(1.5)
