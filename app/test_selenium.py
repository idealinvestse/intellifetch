from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_chromedriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=chrome_options)
    driver.get("https://www.google.com")
    assert "Google" in driver.title
    driver.quit()

if __name__ == "__main__":
    test_chromedriver()
    print("Chromedriver fungerar korrekt.")