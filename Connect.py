import os
import time
import random
import logging
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


# Load environment variables from .env file
load_dotenv()

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve the username, password, ChromeDriver path, and search URL from environment variables
USERNAME = os.getenv('LINKEDIN_USERNAME')
PLAIN_TEXT_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
SEARCH_URL = os.getenv('SEARCH_URL')

if not USERNAME or not PLAIN_TEXT_PASSWORD or not CHROMEDRIVER_PATH or not SEARCH_URL:
    logging.error("One or more required environment variables are missing")
    exit(1)

# Hash the password (for demonstration purposes; you typically wouldn't hash it like this)
hashed_password = hashlib.sha256(PLAIN_TEXT_PASSWORD.encode()).hexdigest()

# Set up ChromeDriver options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start Chrome maximized
chrome_options.add_argument("--disable-extensions")  # Disable extensions for consistency

# Set up ChromeDriver
driver_service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

# Function to log in and navigate directly to the search page
def login_and_navigate():
    logging.info("Navigating to LinkedIn login page")
    driver.get(SEARCH_URL)
    logging.info("Entering username and password")
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")

    # Enter the username
    username_field.send_keys(USERNAME)

    # Use the plain text password
    password_field.send_keys(PLAIN_TEXT_PASSWORD)

    # Submit the login form
    logging.info("Submitting the login form")
    password_field.send_keys(Keys.RETURN)

    # Wait for login to process
    random_delay()
    
    logging.info(f"Navigating to search results page: {SEARCH_URL}")
    random_delay()

# Function to add a random delay
def random_delay():
    delay = random.uniform(3, 7)
    logging.info(f"Waiting for {delay:.2f} seconds")
    time.sleep(delay)

# Function to highlight buttons
def highlight_buttons():
    logging.info("Highlighting buttons")
    try:
        # Define XPath for different buttons
        button_selectors = {

            'connect': "//button[contains(@aria-label, 'Connect') or contains(@aria-label, 'connect')]",
            'follow': "//button[contains(@aria-label, 'Follow') or contains(@aria-label, 'follow')]",
            'pending': "//button[contains(@aria-label, 'Pending') or contains(@aria-label, 'pending')]",
            'message': "//button[contains(@aria-label, 'Message') or contains(@aria-label, 'message')]"
        }

        for button_type, xpath in button_selectors.items():
            buttons = driver.find_elements(By.XPATH, xpath)
            if not buttons:
                logging.warning(f"No {button_type} buttons found to highlight")
            for button in buttons:
                button_text = button.get_attribute('aria-label').lower()
                color = ""
                if 'connect' in button_text:
                    button.click()
                    color = "green"

                    try:
                        time.sleep(1)
                        send_now_button = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[3]/button[2]")
                        send_now_button.click()
                    except NoSuchElementException:
                        print("Could not find 'Send now' button. Skipping...")
                        continue
                else:
                    continue
                if color:
                    driver.execute_script(f"arguments[0].style.backgroundColor = '{color}'", button)
                    driver.execute_script("arguments[0].style.border = '2px solid black'", button)
                    logging.info(f"Highlighted {button_text} button with color {color}")

                # Random delay between actions
                random_delay()
    except Exception as e:
        logging.error(f"Error during button highlighting: {e}")

def handle_pagination():
    start_time = time.time()
    min_runtime = 600  # 10 minutes in seconds

    while True:
        logging.info("Highlighting buttons on the current page")
        highlight_buttons()

        time_elapsed = time.time() - start_time
        if time_elapsed >= min_runtime:
            logging.info("10 minutes have passed. Exiting.")
            break

        next_button_found = False
        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            try:
                # Find the 'Next' button or a link to navigate to the next page
                next_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Next')]")
                if next_button.is_enabled():
                    logging.info("Navigating to the next page")
                    next_button.click()
                    random_delay()
                    next_button_found = True
                    break
                else:
                    logging.warning("Next button is not enabled. Trying again.")
                    retry_count += 1
                    time.sleep(2)  # Wait before retrying
            except Exception as e:
                logging.error(f"Error navigating to the next page: {e}")
                retry_count += 1
                time.sleep(2)  # Wait before retrying

        if not next_button_found:
            logging.info("No more pages to navigate or failed to locate the 'Next' button after several retries.")
            break

# Perform login and navigate to the search results page
login_and_navigate()

# Handle pagination and highlight buttons on each page
handle_pagination()

# Keep the browser open for a while to observe changes
random_delay()

# Close the browser
logging.info("Closing the browser")
driver.quit()

