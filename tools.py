import random
from time import sleep
import requests
from bs4 import BeautifulSoup
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class UserAgents:
    def agents(self):
        with open('user-agents.txt') as file:
            texts = file.read().split("\n")
            return random.choice(texts)


class JbHiFi:
    def __init__(self, website_url):
        self.website_url = website_url
        self.req = requests.get(website_url, headers={"User-Agent":UserAgents().agents()})
    

    def allProductLinks(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=3*1000)
            page = browser.new_page(user_agent=UserAgents().agents())

            print("Initiating the Automation | Powered by Playwright.")
            page.goto(self.website_url)
            page.wait_for_url(self.website_url, timeout=1*1000)

            page.keyboard.press("PageDown")

            # xpath for displaying the number of products per page. This one is for 100 products per page.
            page_size_xpath = """//*[@id="collection-container"]/div[4]/div/div[2]/ul/li[4]/a"""
            
            try:                
                page.wait_for_selector(page_size_xpath, timeout=1*10000)
                page.query_selector(page_size_xpath).click()            
            except PlaywrightTimeoutError:
                print("Content loading error! Please wait few seconds and run the script again.")
                sleep(3)
                sys.exit()

            
            # for load more button
            button_xpath = """//button[@class='load-more-button']"""
            page.wait_for_selector(button_xpath, timeout=1*100000)

            total_results = round(float(page.query_selector("//div[@class='infinite-hits-text']").inner_text().split()[3]) / 100, 0)
            print(f"Estimated number of pages to scrape | {total_results} pages.")

            # Infinite click until the bottom of the page.
            for clicks in range (1, int(total_results)+2):
                try:
                    print(f"Scraping | page number {clicks}.")
                    page.wait_for_timeout(timeout=3*1000)           
                    page.query_selector(button_xpath).click()
                    page.keyboard.press("PageUp")
                except AttributeError:
                    break
            
            

            links_xpath = "//a[@class='ais-details-a product-tile']"            
            page.wait_for_selector(links_xpath, timeout=1*10000)

            content = page.content()
            soup = BeautifulSoup(content, 'lxml')

            # total_results = float(soup.find('div', class_='infinite-hits-text').text.strip().split()[3]) / 36
            
            ##### Prouduct datas #####
            category_name = soup.find('div', id='collection-container').find('h1').text.strip()
            all_names = [title.get('title') for title in soup.find_all('a', class_='ais-details-a product-tile')]
            all_prices = [price.text.strip() for price in soup.find_all('div', class_='pricing-block')]
            all_links = [f"https://www.jbhifi.com.au{link.get('href')}" for link in soup.find_all('a', class_='ais-details-a product-tile')]
            all_images = [link.get('src') for link in soup.find_all('img', class_='product-tile__image')]
            print("Done!")
            browser.close()
            #############################

            return category_name, all_names, all_prices, all_links, all_images