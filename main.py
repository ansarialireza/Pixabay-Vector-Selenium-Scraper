import os
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class PixabayScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.download_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "downloaded_data")
        self.driver = webdriver.Chrome()  # Initialize Chrome WebDriver

    def create_folders(self, categories):
        os.makedirs(self.download_path, exist_ok=True)
        for category in categories:
            category_path = os.path.join(self.download_path, category)
            os.makedirs(category_path, exist_ok=True)

    def scrape_metadata(self, url):
        self.driver.get(url)
        metadata_list = []

        try:
            WebDriverWait(self.driver, 30).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'item')))
        except TimeoutException:
            print("Timeout exception occurred while waiting for elements. Continuing with the program.")

        items = self.driver.find_elements(By.CLASS_NAME, 'item')  # اصلاح این خط
        for item in items:
            title = item.find_element(By.CLASS_NAME, 'title').text.strip()  # اصلاح این خط
            tags = [tag.text.strip() for tag in item.find_elements(By.CLASS_NAME, 'tag')]  # اصلاح این خط
            creator = item.find_element(By.CLASS_NAME, 'creator').text.strip()  # اصلاح این خط
            vector_file_url = item.find_element(By.CSS_SELECTOR, 'a.download')['href']  # اصلاح این خط

            metadata = {
                'Title': title,
                'Tags': ', '.join(tags),
                'Creator': creator,
                'Vector File URL': vector_file_url,
                'Other Metadata': ''  # Add other relevant metadata
            }
            metadata_list.append(metadata)

        return metadata_list


    def download_vector_graphics(self, metadata_list, category):
        for metadata in metadata_list:
            vector_file_url = metadata['Vector File URL']
            self.driver.get(vector_file_url)

            try:
                WebDriverWait(self.driver, 30).until(lambda d: d.execute_script("return document.readyState === 'complete'"))
            except TimeoutException:
                print("Timeout exception occurred while waiting for the file to download. Continuing with the program.")

            # Rename and move the downloaded file to the category folder
            filename = os.path.join(self.download_path, category, f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png")  # تغییر این خط
            os.rename(self.get_downloads_path(), filename)

    def get_downloads_path(self):
        # Function to get the path of the most recent download
        downloads_path = os.path.expanduser("~/Downloads")
        newest_file = max([os.path.join(downloads_path, f) for f in os.listdir(downloads_path)], key=os.path.getctime)
        return newest_file

    def generate_csv(self, category, metadata_list):
        csv_file_path = os.path.join(self.download_path, category, f"{category}_metadata.csv")

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['Title', 'Tags', 'Creator', 'Vector File URL', 'Other Metadata']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for metadata in metadata_list:
                writer.writerow(metadata)

    def scrape_and_download_category(self, category):
        category_url = f"{self.base_url}/vectors/search/{category}/"
        metadata_list = self.scrape_metadata(category_url)
        self.download_vector_graphics(metadata_list, category)
        self.generate_csv(category, metadata_list)

    def scrape_and_download_all_categories(self, categories):
        for category in categories:
            self.scrape_and_download_category(category)

    def summarize_results(self, categories):
        print("\nSummary Report:")
        for category in categories:
            category_folder = os.path.join(self.download_path, category)
            files_in_category = [f for f in os.listdir(category_folder) if os.path.isfile(os.path.join(category_folder, f))]
            vector_count = len(files_in_category) - 1  # Exclude the CSV file

            print(f"{category.capitalize()}: {vector_count} vector graphics downloaded.")

    def close_driver(self):
        self.driver.quit()  # Close the WebDriver

def main():
    base_url = "https://pixabay.com"
    categories = ['money',]

    # Phase 1: Serial Implementation
    serial_scraper = PixabayScraper(base_url)
    serial_scraper.create_folders(categories)
    start_time_serial = datetime.now()
    serial_scraper.scrape_and_download_all_categories(categories)
    end_time_serial = datetime.now()
    print(f"Serial Execution Time: {end_time_serial - start_time_serial}")

    # Phase 2: Multithreaded Implementation
    threaded_scraper = PixabayScraper(base_url)
    threaded_scraper.create_folders(categories)
    start_time_threaded = datetime.now()
    threaded_scraper.scrape_and_download_all_categories(categories)
    end_time_threaded = datetime.now()
    print(f"Multithreaded Execution Time: {end_time_threaded - start_time_threaded}")

    # Analyze and compare performance
    serial_scraper.summarize_results(categories)
    threaded_scraper.summarize_results(categories)

    # Close WebDriver instances
    serial_scraper.close_driver()
    threaded_scraper.close_driver()

if __name__ == "__main__":
    main()
