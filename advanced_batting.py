import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Configure ChromeOptions
options = webdriver.ChromeOptions()

# Set up the ChromeDriver service
service = ChromeService(executable_path=ChromeDriverManager().install())

# Set up the selenium webdriver
driver = webdriver.Chrome(service=service, options=options)

# URL of the page to scrape
url = 'https://www.baseball-reference.com/leagues/majors/2024-advanced-batting.shtml'

# Open the URL
driver.get(url)

# Handle cookie consent if present
try:
    cookie_consent_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
    )
    cookie_consent_button.click()
    print("Cookie consent accepted.")
except Exception as e:
    print("No cookie consent prompt found or failed to accept it.")

# Wait for the parent div to be present
try:
    parent_div = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'div_players_advanced_batting'))  # Replace 'parent_div_id' with the actual ID
    )
    print("Parent div found")

    # Wait for the table within the parent div to be visible
    table = WebDriverWait(parent_div, 60).until(
        EC.presence_of_element_located((By.ID, 'players_advanced_batting'))  # Replace 'table_id' with the actual ID
    )
    print("Table found")

    # Scraping the table into a DataFrame
    df = pd.read_html(table.get_attribute('outerHTML'))[0]

    # Print the DataFrame for debugging
    print("DataFrame from table:")
    print(df.head())

except NoSuchElementException as e:
    print("Element not found:", e)
except TimeoutException as e:
    print("Timeout while waiting for the table:", e)
finally:
    driver.quit()

# Load the existing CSV file (if exists) or create a new DataFrame
csv_path = '/Users/casha/Desktop/MLB Data Model/mlb_advanced_batting_stats.csv'
try:
    existing_df = pd.read_csv(csv_path)
    print("Existing CSV file loaded.")
except FileNotFoundError:
    existing_df = pd.DataFrame()

# Attempt to append the new data to the existing DataFrame
try:
    updated_df = pd.concat([existing_df, df], ignore_index=True)
    updated_df.to_csv(csv_path, index=False)
    print(f"CSV file updated and saved at: {csv_path}")

    # Display the updated DataFrame
    print(updated_df.head())

except NameError:
    print("Error: DataFrame 'df' is not defined.")
except Exception as e:
    print("Error appending data to CSV:", e)
