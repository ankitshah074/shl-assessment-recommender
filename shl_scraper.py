

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time

def setup_driver():
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def scrape_catalog_selenium():
    
    driver = setup_driver()
    all_assessments = []
    base_url = "https://www.shl.com/products/product-catalog/"
    
    print("Starting Selenium scraping...")
    print("=" * 60)
    
    try:
        # Load first page to check structure
        driver.get(base_url + "?type=1")
        time.sleep(3)  # Wait for page load
        
        # Find all assessment links
        for page in range(32):
            start = page * 12
            url = f"{base_url}?start={start}&type=1"
            
            print(f"\nPage {page + 1}/32...")
            driver.get(url)
            time.sleep(2)
            
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                
                # Find all rows in table
                rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
                
                for row in rows[1:]:  
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 4:
                           
                            link = cells[0].find_element(By.TAG_NAME, "a")
                            name = link.text.strip()
                            url = link.get_attribute("href")
                            
                            
                            test_type = cells[3].text.strip()
                            
                            assessment = {
                                "name": name,
                                "url": url,
                                "test_type": test_type,
                                "category": "Individual Test Solution"
                            }
                            
                            all_assessments.append(assessment)
                            print(f"  ✓ {name}")
                    
                    except Exception as e:
                        continue
            
            except Exception as e:
                print(f"Error on page {page + 1}: {e}")
                continue
        
    finally:
        driver.quit()
    
    print("\n" + "=" * 60)
    print(f"Total: {len(all_assessments)} assessments")
    print("=" * 60)
    
    return all_assessments



def quick_scrape():
    """Quick scraping without detailed descriptions"""
    assessments = scrape_catalog_selenium()
    
    # Save to JSON
    with open('shl_assessments.json', 'w', encoding='utf-8') as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(assessments)} assessments to shl_assessments.json")
    
    if len(assessments) >= 377:
        print("✓ SUCCESS: Met the 377+ requirement!")
    else:
        print(f"⚠️ WARNING: Only {len(assessments)} found")
    
    return assessments


if __name__ == "__main__":
    
    
    quick_scrape()