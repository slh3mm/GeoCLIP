import os
import time
from dotenv import load_dotenv; load_dotenv();
from seleniumbase import SB
from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

# Initialize Chrome Session
with SB(uc=True, test=True, incognito=True, locale_code="en") as sb:
    # Go to geoguessr.com, enter login info, bypass captcha, click login
    sb.driver.uc_open_with_reconnect("https://www.geoguessr.com/signin")
    sb.uc_gui_click_captcha()
    sb.type('[data-qa="email-field"]', os.environ["UNAME"])
    sb.type('[data-qa="password-field"]', os.environ["PWORD"])
    sb.reconnect(0.1)
    sb.uc_click('[data-qa="login-cta-button"]', reconnect_time=4)

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
        print(game_url)
        
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