# app/scraper.py
import os
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from .config import logger, selectors_config

# Ladda miljövariabler från .env
load_dotenv()

# Dynamisk hantering av Chromedriver-sökväg baserat på operativsystem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DRIVER_PATH = os.path.join(BASE_DIR, "driver", "linux64", "chromedriver") if os.name != 'nt' else os.path.join(BASE_DIR, "driver", "win64", "chromedriver")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", DEFAULT_DRIVER_PATH)

# Kontrollera att chromedriver finns i rätt sökväg
if not os.path.exists(CHROMEDRIVER_PATH):
    logger.error(f"Chromedriver not found at {CHROMEDRIVER_PATH}. Please ensure it exists.")
    raise FileNotFoundError(f"Chromedriver not found at {CHROMEDRIVER_PATH}")


def init_driver() -> webdriver.Chrome:
    """Initialisera en Chrome WebDriver med konfigurationer."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Headless-läge
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
        logger.info("Chrome WebDriver initialized successfully.")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        raise RuntimeError(f"Failed to initialize Chrome WebDriver: {e}")


def fetch_page_source(driver: webdriver.Chrome, url: str) -> str:
    """Navigera till en URL och hämta sidkällan."""
    try:
        logger.info(f"Navigating to URL: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "merinfo-content"))
        )
        logger.info("Page loaded successfully.")
        return driver.page_source
    except Exception as e:
        logger.error(f"Error fetching page source from URL {url}: {e}")
        raise RuntimeError(f"Failed to fetch page source from {url}: {e}")


def extract_data_from_page(soup: BeautifulSoup) -> dict:
    """Extrahera data från HTML-sidan."""
    data = {}

    # Hämta fullständigt namn
    try:
        full_name_tag = soup.select_one(selectors_config.get("person_name"))
        data['full_name'] = full_name_tag.text.strip() if full_name_tag else None
        logger.info(f"Full name extracted: {data['full_name']}")
    except Exception as e:
        logger.error(f"Error extracting full name: {e}")
        data['full_name'] = None

    # Hämta ålder
    try:
        age_tags = soup.select(selectors_config.get("person_age"))
        age_text = next((tag.text.strip().split(' ')[0] for tag in age_tags if 'år' in tag.text.lower()), None)
        data['age'] = age_text
        logger.info(f"Age extracted: {data['age']}")
    except Exception as e:
        logger.error(f"Error extracting age: {e}")
        data['age'] = None

    # Hämta stad
    try:
        city_tag = soup.select_one(selectors_config.get("person_city"))
        data['city'] = city_tag.text.strip() if city_tag else None
        logger.info(f"City extracted: {data['city']}")
    except Exception as e:
        logger.error(f"Error extracting city: {e}")
        data['city'] = None

    # Hämta adress
    try:
        address_tag = soup.select_one(selectors_config.get("person_address"))
        data['address'] = " ".join(address_tag.stripped_strings) if address_tag else None
        logger.info(f"Address extracted: {data['address']}")
    except Exception as e:
        logger.error(f"Error extracting address: {e}")
        data['address'] = None

    # Hämta telefonnummer
    try:
        phone_tag = soup.select_one(selectors_config.get("phone_number"))
        data['phone_number'] = phone_tag.text.strip() if phone_tag else None
        logger.info(f"Phone number extracted: {data['phone_number']}")
    except Exception as e:
        logger.error(f"Error extracting phone number: {e}")
        data['phone_number'] = None

    # Hämta födelsedag
    try:
        birthday_indicator = soup.find('span', class_='mi-font-bold', text=lambda x: x and 'fyller' in x.lower())
        data['birthday'] = birthday_indicator.parent.text.strip() if birthday_indicator else None
        logger.info(f"Birthday extracted: {data['birthday']}")
    except Exception as e:
        logger.error(f"Error extracting birthday: {e}")
        data['birthday'] = None

    # Lägg till andra fält om det krävs

    return data


def scrape_merinfo(first_name: str, last_name: str, city: str) -> dict:
    """Utför scraping för att hämta information om en person."""
    query = f"{first_name}+{last_name}+{city}"
    search_url = f"https://www.merinfo.se/search?q={query}"

    driver = init_driver()
    try:
        # Hämta sidans HTML
        page_source = fetch_page_source(driver, search_url)

        # Skapa BeautifulSoup-objekt
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extrahera data
        data = extract_data_from_page(soup)
        logger.info(f"Data extracted successfully: {json.dumps(data, ensure_ascii=False)}")
        return data
    except Exception as e:
        logger.error(f"Scraping process failed: {e}")
        raise e
    finally:
        driver.quit()
        logger.info("Driver closed.")
