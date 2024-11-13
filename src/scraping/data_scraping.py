import os
import time
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from seleniumbase import SB
from selenium.webdriver.common.action_chains import ActionChains

load_dotenv()


# Initialize Chrome Session
# with SB(uc=True, incognito=True, locale_code="en") as sb:
with SB(uc=True, incognito=False, locale_code="en") as sb:

    # Go to geoguessr.com, enter login info, bypass captcha, click login
    sb.driver.uc_open_with_reconnect("https://www.geoguessr.com/signin")

    # Not always needed for some reason
    sb.driver.uc_gui_click_captcha()

    # Enter login info automatically
    # sb.type('[data-qa="email-field"]', os.environ["UNAME"])
    # sb.type('[data-qa="password-field"]', os.environ["PWORD"])
    # sb.uc_click('[data-qa="login-cta-button"]', reconnect_time=4)

    # OR Enter login info manually if auto doesn't work
    # sb.driver.uc_gui_press_keys("\t\t\t")
    sb.driver.sleep(5)
    sb.driver.reconnect()
    sb.driver.uc_click('[data-qa="email-field"]')
    sb.driver.uc_gui_press_keys(os.environ["UNAME"])
    sb.driver.uc_gui_press_keys("\t")
    sb.driver.uc_gui_press_keys(os.environ["PWORD"])
    sb.driver.uc_gui_press_keys("\n")

    # Redirect to game page, press play
    # If either of these doesn't work then after logging in, add in sb.sleep() and try going to Classic->World->Play

    # Automatic
    sb.driver.sleep(1.5)
    sb.driver.connect()
    sb.driver.get("https://www.geoguessr.com/maps/world/play")
    # sb.driver.click('[data-qa="start-game-button"]')

    # Manual approach
    # driver.uc_gui_press_keys("\t\t\t\t\t\t\t\n")
    sb.driver.quit()
    sb.sleep(15)

    # Play N_GAMES games, each with 5 rounds
    N_GAMES = 5000
    SAVE_RATE = 5
    game_id_buffer = ""
    print("Starting game loop")
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
