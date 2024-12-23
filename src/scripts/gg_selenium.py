import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# Change chrome driver path accordingly
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

# Redirect to game page, press play
time.sleep(1)
driver.get("https://www.geoguessr.com/maps/world/play")
play_button = wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'button[data-qa="start-game-button"]')
    )
)
play_button.click()

# Wait for game to load
wait.until(EC.url_contains("/game/"))

# Play N_GAMES games, each with 5 rounds
N_GAMES = 1000
SAVE_RATE = 1
game_id_buffer = ""
for game in range(N_GAMES):
    # Grab game url and game id
    game_url = driver.current_url
    game_id = game_url.split("/")[-1]
    game_id_buffer += game_id + "\n"
    print(game_id)

    # Save game_id every SAVE_RATE games
    if (game + 1) % SAVE_RATE == 0:
        with open("game_ids.txt", "a") as f:
            f.write(f"{game_id_buffer}")
            f.close()
        game_id_buffer = ""

    # Play the 5 rounds of a game
    for round in range(5):
        guess_map_element = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-qa="guess-map"]'))
        )
        guess_map_element.click()

        guess_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-qa="perform-guess"]')
            )
        )
        guess_button.click()

        next_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-qa="close-round-result"]')
            )
        )
        next_button.click()

    # Start new game
    play_again_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-qa="play-again-button"]')
        )
    )
    play_again_button.click()

    # Wait for new game to load
    wait.until(lambda driver: driver.current_url != game_url)

# Exit safely
driver.quit()
