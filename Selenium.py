import time
import os
import xlwt
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import  Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

chrome_options = Options()
path = r"D:\App exe\chromedriver-win64\chromedriver.exe"
ser = Service(path)

browser =  webdriver.Chrome(service=ser)
wait = WebDriverWait(browser, 10)
browser.get("https://batdongsan.com.vn/nha-dat-ban/p49")
#browser.maximize_window()
time.sleep(5)

eles = browser.find_elements(By.XPATH,'//div[@class="re__card-info-content"]')

# Initialize the Excel workbook and sheet
workbook = xlwt.Workbook()  
sheet = workbook.add_sheet('Property Data')  

# Define column titles, 
columns = ["Agent", "Title",  "Date posted", "Price", "Area", "Price per Area", "Bedrooms", "Toilets", "Description", "Direction", "Location", "URLS_Img_1", "URLS_Img_2", "URLS_Img_3", "URLS_Img_4", "Link posted"]
for i, column in enumerate(columns):
    sheet.write(0, i, column)  # Write the column headers

def download_image(url, path_to_save):
    """
    Download an image from a given URL and save it to a specified path.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the response was an error
        
        with open(path_to_save, 'wb') as f:
            f.write(response.content)
    except requests.RequestException as e:
        print(f"Failed to download {url}. Reason: {e}")

def get_element_text_or_default(parent, xpath, default="0"):
    try:
        return parent.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        return default

# Initialize row index for Excel
row_index = 1

for ele in eles:
    # Extract the data
    name_proj = get_element_text_or_default(ele, './/span[@class="pr-title js__card-title"]', "N/A")
    price_proj = get_element_text_or_default(ele, './/span[@class="re__card-config-price js__card-config-item"]', "N/A")
    area_proj = get_element_text_or_default(ele, './/span[@class="re__card-config-area js__card-config-item"]', "N/A")
    price_per_area = get_element_text_or_default(ele, './/span[@class="re__card-config-price_per_m2 js__card-config-item"]', "N/A")
    beds_proj = get_element_text_or_default(ele, './/span[contains(@class, "re__card-config-bedroom")]/span', "N/A")
    wc_proj = get_element_text_or_default(ele, './/span[contains(@class, "re__card-config-toilet")]/span', "N/A")
    #location_text = get_element_text_or_default(ele, './/div[contains(@class, "re__card-location")]/span[2]', "N/A") #[PAGE 1-18]
    location_text = get_element_text_or_default(ele, './/div[@class="re__card-location"]/span', "N/A")
    des_proj = get_element_text_or_default(ele, './/div[@class="re__card-description js__card-description"]', "N/A")

    contact_ele = ele.find_element(By.XPATH, './/ancestor::div[contains(@class, "re__card")]//div[@class="re__card-contact"]')
    date_span = contact_ele.find_element(By.XPATH, './/span[@class="re__card-published-info-published-at"]')
    date = date_span.get_attribute("aria-label")
    #agent_name = "N/A" #If cards don't have agent name [Page 66+]
    direction = "N/A"

    
    # Extract Date and Agent Name (for cards that have agent namen)
    agent_name_ele = contact_ele.find_element(By.XPATH, './/div[contains(@class, "re__card-published-info-agent-profile-name")]')
    agent_name = agent_name_ele.text.strip()
    

     # Write the basic data to the Excel sheet
    data = [agent_name, name_proj, date, price_proj, area_proj, price_per_area, beds_proj, wc_proj, des_proj, direction, location_text] 

    # Extract and append image URLs
    images = ele.find_elements(By.XPATH, './/ancestor::div[contains(@class, "re__card")]//img')
    img_urls = []
    for img in images[:4]:  # Adjust the slice as per the number of images you wish to capture
        img_url = img.get_attribute('src') if img.get_attribute('src') else img.get_attribute('data-src')
        img_urls.append(img_url)
    """# Extract and append image URLs
    for index, img in enumerate(images[:4], start=1):  # Adjust as per the number of images
        img_url = img.get_attribute('src') if img.get_attribute('src') else img.get_attribute('data-src')
        img_urls.append(img_url)
        
        # Define a path to save the image
        image_path = f"D:\DOWNLOADS\Crawl_batdongsan\Image\Property_{row_index}_Image_{index}.jpg"
        download_image(img_url, image_path)"""
    # Extend the data list with the image URLs
    data.extend(img_urls + ["N/A"] * (4 - len(img_urls)))  # Ensure there are always 4 URL fields

    # Extract the property link  
    property_link_element = ele.find_element(By.XPATH, './/ancestor::div[contains(@class, "re__card")]//a[contains(@class, "js__product-link-for-product-id")]')
    property_link = property_link_element.get_attribute('href')
    data.append(property_link)

    print(data)
    print("===========================================================================================")

    for i, value in enumerate(data):
        sheet.write(row_index, i, value)

    row_index += 1  # Move to the next row in the Excel sheet

# Save the workbook
workbook.save(r'D:\NCKH\Batdongsan_Crawler\Output_dataset\Bonus Data\D5\PD_49.xls')  # Save the Excel file
browser.quit()  # Close the browser after scraping is done

