import os
import sys
from dotenv import load_dotenv

from seleniumbase import SB, Driver
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

sys.argv.append("-n")


def scrape_geoguessr(id):
    # Initialize Chrome Session
    driver = Driver(uc=True, incognito=True, locale_code="en")
    try:
        # Go to geoguessr.com, enter login info, bypass captcha, click login
        driver.uc_open_with_reconnect(
            r"https://www.geoguessr.com/signin?target=%2Fmaps%2Fworld%2Fplay"
        )
        
        # Not always needed for some reason
        driver.uc_gui_click_captcha()

        # Enter login info automatically
        driver.type('[data-qa="email-field"]', os.environ["UNAME"])
        driver.type('[data-qa="password-field"]', os.environ["PWORD"])
        driver.uc_click('[data-qa="login-cta-button"]', reconnect_time=4)

        # OR Enter login info manually if auto doesn't work
        # driver.uc_gui_press_keys("\t\t\t")
        # driver.uc_gui_press_keys(os.environ["UNAME"])
        # driver.uc_gui_press_keys("\t")
        # driver.uc_gui_press_keys(os.environ["PWORD"])
        # driver.uc_gui_press_keys("\t\t\t\t\n")

        # Redirect to game page, press play
        # If either of these doesn't work then after logging in, try going to Classic, then World, then pressing play after
        
        # Automatic
        driver.get("https://www.geoguessr.com/maps/world/play")
        driver.click('[data-qa="start-game-button"]')
        
        # Manual approach
        # driver.uc_gui_press_keys("\t\t\t\t\t\t\t\n")
        
        driver.sleep(10)

        # Play N_GAMES games, each with 5 rounds
        N_GAMES = 2000
        SAVE_RATE = 5
        game_id_buffer = ""
        print("Starting Games")
        for game in range(N_GAMES):
            # Grab game url and game id
            game_url = driver.get_current_url()
            game_id = game_url.split("/")[-1]
            game_id_buffer += game_id + "\n"

            # Save game_id every SAVE_RATE games
            if game % SAVE_RATE == 0:
                with open("game_ids.txt", "a") as f:
                    f.write(f"{game_id_buffer}")
                    f.close()
                game_id_buffer = ""

            # Play the 5 rounds of a game
            for round in range(5):
                driver.click('[data-qa="guess-map"]')
                driver.click('[data-qa="perform-guess"]')
                driver.click('[data-qa="close-round-result"]')

            # Start new game
            driver.click('[data-qa="play-again-button"]')
            driver.sleep(1.5)
    finally:
        driver.quit()


# Run N_GAMES for each of the N_WORKERS workers
N_WORKERS = 1
with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
    for id in range(N_WORKERS):
        executor.submit(scrape_geoguessr, id)
