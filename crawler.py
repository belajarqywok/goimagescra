import os
import re
import time
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from concurrent.futures import ThreadPoolExecutor

class BrowserFactory:
    @staticmethod
    def create_browser():
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument("window-size=1200x600")
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--allow-cross-origin-auth-prompt')
        return webdriver.Chrome(options=options)

class ImageCrawler:
    def __init__(self, browser, target):
        self.browser = browser
        self.target = target

    def save_image(self, img_src, dirname):
        response = requests.get(url=img_src)
        if response.status_code == 200:
            filename = os.path.join(dirname, os.path.basename(img_src))
            with open(filename, "wb") as file:
                file.write(response.content)

    def crawl_images(self, search_query, dirname):
        search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={search_query}"
        self.browser.get(search_url)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for iter in range(self.target):
                try:
                    img_box_xpath = f'//*[@id="islrg"]/div[1]/div[{iter + 1}]/a[1]/div[1]/img'
                    img_box = self.browser.find_element('xpath', img_box_xpath)
                    img_box.click()

                    for _ in range(2):
                        fir_img_xpath = '//*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img'
                        fir_img = self.browser.find_element('xpath', fir_img_xpath)

                        time.sleep(3)
                        ActionChains(self.browser).move_to_element(fir_img).perform()
                        ActionChains(self.browser).move_to_element(fir_img).perform()

                    url_pattern = r"https?://[^?]+"
                    url = re.findall(url_pattern, fir_img.get_attribute('src'))
                    print(f"Image: {url[0]}")
                    
                    future = executor.submit(self.save_image, url[0], dirname)
                    futures.append(future)

                    if not bool((iter + 1) % 5):
                        self.browser.execute_script("window.scrollBy(0, 300);")

                except NoSuchElementException:
                    print("[ WAIT.... ]")
                finally:
                    time.sleep(15)
                    continue

            for future in futures:
                future.result()

if __name__ == "__main__":
    PARAMS = {
        'cats': [
            'cat cataract',
            'cat cataract image'
        ],
        'dogs': [
            'dog cataract',
            'dog cataract image'
        ]
    }

    TARGET = 50

    for key_param, val_param in PARAMS.items():
        DIR_NAME = f"datasets/{key_param}"
        os.makedirs(
            name=DIR_NAME,
            exist_ok=True
        )

        browser = BrowserFactory.create_browser()
        image_crawler = ImageCrawler(browser, TARGET)

        for param in val_param:
            image_crawler.crawl_images(
                search_query=param,
                dirname=DIR_NAME
            )

        browser.quit()
