# app/scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import json
from .config import logger, selectors_config
from dotenv import load_dotenv

load_dotenv()

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver")  # Default if not specified

def scrape_merinfo(first_name: str, last_name: str, city: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)

    try:
        query = f"{first_name}+{last_name}+{city}"
        search_url = f"https://www.merinfo.se/search?q={query}"
        logger.info(f"Navigating to search URL: {search_url}")
        driver.get(search_url)

        wait = WebDriverWait(driver, 10)

        # Vänta tills sökresultaten är laddade
        first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors_config.get("search_result_link"))))
        logger.info("Clicking on the first search result.")
        first_result.click()

        # Vänta tills personens sida är laddad
        wait.until(EC.presence_of_element_located((By.ID, "merinfo-content")))
        logger.info("Person's page loaded.")

        # Hämta sidans HTML
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        data = {}

        # Hämta fullständigt namn
        try:
            full_name_tag = soup.select_one(selectors_config.get("person_name"))
            full_name = full_name_tag.text.strip() if full_name_tag else None
            data['full_name'] = full_name
            logger.info(f"Full name: {full_name}")
        except Exception as e:
            logger.error(f"Error fetching full name: {e}")
            data['full_name'] = None

        # Hämta ålder
        try:
            age_tags = soup.select(selectors_config.get("person_age"))
            age_text = None
            for tag in age_tags:
                text = tag.text.lower()
                if 'årig' in text or 'år ' in text:
                    age_text = tag.text.strip().split(' ')[0]
                    break
            data['age'] = age_text
            logger.info(f"Age: {age_text}")
        except Exception as e:
            logger.error(f"Error fetching age: {e}")
            data['age'] = None

        # Hämta stad
        try:
            city_tag = soup.select_one(selectors_config.get("person_city"))
            city_text = city_tag.text.strip() if city_tag else None
            data['city'] = city_text
            logger.info(f"City: {city_text}")
        except Exception as e:
            logger.error(f"Error fetching city: {e}")
            data['city'] = None

        # Hämta adress
        try:
            address_tag = soup.select_one(selectors_config.get("person_address"))
            address = " ".join(address_tag.stripped_strings) if address_tag else None
            data['address'] = address
            logger.info(f"Address: {address}")
        except Exception as e:
            logger.error(f"Error fetching address: {e}")
            data['address'] = None

        # Hämta telefonnummer
        try:
            phone_tag = soup.select_one(selectors_config.get("phone_number"))
            phone_number = phone_tag.text.strip() if phone_tag else None
            data['phone_number'] = phone_number
            logger.info(f"Phone number: {phone_number}")
        except Exception as e:
            logger.error(f"Error fetching phone number: {e}")
            data['phone_number'] = None

        # Hämta födelsedag
        try:
            birthday_indicator = soup.find('span', class_='mi-font-bold', text=lambda x: x and 'fyller' in x.lower())
            if birthday_indicator:
                birthday_text = birthday_indicator.parent.text.strip()
                data['birthday'] = birthday_text
                logger.info(f"Birthday: {birthday_text}")
            else:
                data['birthday'] = None
        except Exception as e:
            logger.error(f"Error fetching birthday: {e}")
            data['birthday'] = None

        # Hämta personnummer
        try:
            pnr_div = soup.find('div', attrs={'dusk': 'summery-pnr'})
            if pnr_div:
                h3_tag = pnr_div.find('h3')
                if h3_tag and h3_tag.next_sibling:
                    personnummer = h3_tag.next_sibling.strip()
                    data['national_id'] = personnummer
                    logger.info(f"National ID: {personnummer}")
                else:
                    data['national_id'] = None
            else:
                data['national_id'] = None
        except Exception as e:
            logger.error(f"Error fetching national ID: {e}")
            data['national_id'] = None

        # Hämta civilstatus
        try:
            marital_tag = soup.find('h3', string=selectors_config.get("marital_status_header"))
            if marital_tag:
                marital_status = marital_tag.find_next_sibling(text=True).strip()
                data['marital_status'] = marital_status
                logger.info(f"Marital Status: {marital_status}")
            else:
                data['marital_status'] = None
        except Exception as e:
            logger.error(f"Error fetching marital status: {e}")
            data['marital_status'] = None

        # Extrahera personkopplingar (Cohabitants)
        try:
            cohabitants = []
            cohabitants_section = soup.find(lambda tag: tag.name == "h3" and "Personer som bor på adressen" in tag.text)
            if cohabitants_section:
                cohabitants_table = cohabitants_section.find_next('ul', class_='list-timeline')
                if cohabitants_table:
                    for li in cohabitants_table.find_all('li', class_='list-timeline-item'):
                        name_tag = li.find('a', class_='mi-text-primary')
                        name = name_tag.text.strip() if name_tag else 'N/A'
                        age = li.find(text=lambda x: 'år' in x.lower())
                        age = age.strip() if age else 'N/A'
                        cohabitants.append({
                            'name': name,
                            'age': age
                        })
            data['cohabitants'] = cohabitants
            logger.info(f"Cohabitants: {cohabitants}")
        except Exception as e:
            logger.error(f"Error fetching cohabitants: {e}")
            data['cohabitants'] = []

        # Extrahera fordon (Vehicles)
        try:
            vehicles = []
            vehicle_section = soup.find(lambda tag: tag.name == "h3" and "Fordon på adressen" in tag.text)
            if vehicle_section:
                vehicle_table = vehicle_section.find_next('vehicle-table')
                if vehicle_table:
                    # Antag att v-bind:numbers är en JSON-sträng
                    vehicle_items = vehicle_table.get('v-bind:numbers', '[]')
                    try:
                        # Rensa enkla felaktiga citationstecken eller andra problem
                        vehicles_data = json.loads(vehicle_items.replace("'", '"'))
                        for v in vehicles_data:
                            vehicles.append({
                                'make_model': v.get('display', ''),
                                'model_year': v.get('model_year', ''),
                                'owner': v.get('owner', ''),
                                'registration': v.get('registration', '')
                            })
                    except json.JSONDecodeError:
                        logger.error("Error parsing vehicle JSON data.")
            data['vehicles'] = vehicles
            logger.info(f"Vehicles: {vehicles}")
        except Exception as e:
            logger.error(f"Error fetching vehicles: {e}")
            data['vehicles'] = []

        # Extrahera företagsengagemang (Company Engagements)
        try:
            companies = []
            company_section = soup.find(lambda tag: tag.name == "h2" and "jobb & styrelseuppdrag" in tag.text.lower())
            if company_section:
                companies_table = company_section.find_next('board-table')
                if companies_table:
                    company_items = companies_table.get('v-bind:boards', '[]')
                    try:
                        # Rensa enkla felaktiga citationstecken eller andra problem
                        companies_data = json.loads(company_items.replace("'", '"'))
                        for c in companies_data:
                            companies.append({
                                'company_name': c.get('name', ''),
                                'position': c.get('position', ''),
                                'company_url': c.get('url', '')
                            })
                    except json.JSONDecodeError:
                        logger.error("Error parsing company engagements JSON data.")
            data['companies'] = companies
            logger.info(f"Company Engagements: {companies}")
        except Exception as e:
            logger.error(f"Error fetching company engagements: {e}")
            data['companies'] = []

        return data