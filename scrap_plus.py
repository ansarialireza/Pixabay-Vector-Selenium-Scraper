from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urljoin
import threading
import time

# مسیر ذخیره تصاویر (پوشه کناری اسکریپت)
download_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")

# اطمینان از وجود پوشه
os.makedirs(download_path, exist_ok=True)

# مسیر درایور مرورگر (Chrome در اینجا)

# ایجاد درایور
driver = webdriver.Chrome()

# شماره صفحه ابتدایی
page_number = 1

# Function to download an image
def download_image(img_url, filename):
    try:
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")

while True:
    # آدرس سایت با شماره صفحه فعلی
    url = f"https://pixabay.com/vectors/search/?order=ec&pagi={page_number}"

    # باز کردن سایت
    driver.get(url)

    # Wait for the "Accept" button and click it
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
        )
        accept_button.click()
    except Exception as e:
        print(f"Error clicking on the 'Accept' button: {e}")

    # Perform smooth scrolling to the bottom of the page using JavaScript
    current_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

    while True:
        # Simulate smooth scrolling using JavaScript
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust the sleep time according to your preference

        new_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

        # Break the loop if no more scrolling is possible (reached the bottom)
        if new_height == current_height:
            break

        current_height = new_height

    # Wait for the image elements to be present
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.container--MwyXl a.link--WHWzm img')))

    # گرفتن لینک‌های تصاویر با استفاده از BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    image_elements = soup.select('.container--MwyXl a.link--WHWzm img')

    # Download images in parallel
    threads = []
    for i, img_element in enumerate(image_elements):
        img_url = img_element['src']
        if not img_url.startswith(('http:', 'https:')):
            img_url = urljoin(url, img_url)
        
        filename = os.path.join(download_path, f"image_{(page_number - 1) * 30 + i + 1}.png")
        thread = threading.Thread(target=download_image, args=(img_url, filename))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # افزایش شماره صفحه
    page_number += 1
