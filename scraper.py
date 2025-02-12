import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

tickers = ["CVS", "D", "VRT", "EXC", "WAB", "KHC", "MLM", "GOLD", "SW", "WAT", "BAM", "QSR", "BIIB", "NI", "THC", "GMAB", "IPG", "LAD", "GNRC", "COOP", "R", "TMHC", "SITE", "ALKS", "CAMT", "BXMT", "SLVM", "UE", "SAH", "CHEF", "PAX", "DBD", "PX", "KRNT", "CIM", "RDWR", "HCSG", "AVXL", "CNDT", "SPTN", "MLYS", "GILT", "DENN", "BIOX", "OTLY", "VPG", "RDCM", "RGS", "PODC", "CRWS", "NMTC", "PYPD", "SPMC"]

data = []

for ticker in tickers:
    try:
        # Set up the Chrome driver once
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        page_url = f"https://marketchameleon.com/Overview/{ticker}/Earnings/Earnings-Charts"
        driver.get(page_url)

    #     # Extract elements
    #     description_elements = driver.find_elements(By.CLASS_NAME, "symbol-section-header-descr")
    #     description = description_elements[0].text
    #     match = re.search(r"(\d+)%\s+of the time in the last (\d+)\s+quarters", description)

    #     if match:
    #         percentage, quarters = match.group(1), match.group(2)
    #     else:
    #         percentage, quarters = None, None

    except:
        percentage, quarters = None, None
    
    # data.append((ticker, (percentage, quarters)))

# Close the driver after the loop
driver.quit()

print(data)

