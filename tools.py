import re
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
            browser = p.chromium.launch(headless=True, slow_mo=3*1000)
            page = browser.new_page(user_agent=UserAgents().agents())

            print("Initiating the Automation | Powered by Playwright.")
            page.goto(self.website_url)
            page.wait_for_url(self.website_url, timeout=1*10000)

            # Sometimes the content with products does not show up, so to tackle that the below code exit the script after it's unable to find the main content.
            try:
                main_content = page.query_selector("//div[@class='collection-results-loop']")
            except PlaywrightTimeoutError:
                print("Content loading error! Please wait few seconds and run the script again.")
                sleep(3)
                sys.exit()

            page.keyboard.press("PageDown")

            # xpath for displaying the number of products per page. This one is for 100 products per page.
            try:
                page_size_xpath = """//*[@id="collection-container"]/div[4]/div/div[2]/ul/li[4]/a""" 
                try:               
                    page.query_selector(page_size_xpath).click()
                except AttributeError:
                    pass 
            except PlaywrightTimeoutError:
                pass
            
            try:
                category_name = page.query_selector("//div[@id='collection-container']/h1").inner_text().strip()
                print(f"Product category | {category_name}.")
            except AttributeError:
                print("Content loading error! Please wait few seconds and run the script again.")
                sys.exit()
            
            # For load more button
            button_xpath = """//button[@class='load-more-button']"""      

            # Scraping total results available on the website to estimate the total number of pages to scrape. Estimation may not be accurate.
            try:
                total_results = round(float(page.query_selector("//div[@class='infinite-hits-text']").inner_text().split()[3]) / 100, 0)
            except AttributeError:
                print(f"Content must be different. Url must include all product values with pagination. Please try new url and run the script again.")
                sys.exit()            
            
            if total_results == 0:
                print(f"Estimate number of pages to scrape | 1 page. * Estimation may not be accurate.")
            else:
                print(f"Estimate number of pages to scrape | {int(total_results)} page. * Estimation may not be accurate.")

            # Infinite click until the bottom of the page.
            for clicks in range (1, int(total_results)+100):  # Since I am unable to figure out the total number pages of I just added the extra 100 :D for just a safey measure. The loop breaks after there is more button to click.
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
            
            # up_button = page.query_selector("//button[@class='scroll-up-button']").click()
            page.wait_for_timeout(timeout=5*1000)


            ############################################ Prouduct datas ############################################################################################
            # For price as it has multiple values:
            orginal_price = []
            discount_price = []
            
            price_box = soup.find_all('div', class_='pricing-block')
            for prices in price_box:
                try:
                    orginal_price.append(prices.find('span', class_='ais-hit--price price').text.strip())
                except AttributeError:
                    orginal_price.append(prices.find('s', class_='ais-hit--price-striked').text.strip())

                try:
                    discount_price.append(prices.find('span', class_='sale').text.strip())
                except AttributeError:
                    discount_price.append("N/A")                    

            # For reviews section:
            customer_reviews = []    
            review_datas = soup.find_all('div', class_='ais-hit--details product-tile__details')
            for review in review_datas:
                try:
                    review_ratings = review.find('span', class_='review-rating').text.strip()

                    # Using regular expression to replace bracket charater in review data:
                    review_count = re.sub(r"[\([{})\]]", "", review.find('span', class_='review-count').text.strip())
                    
                    customer_reviews.append(f"{review_ratings}/5 out of {review_count} reviews.")
                except AttributeError:
                    customer_reviews.append("N/A")


            all_names = [title.get('title') for title in soup.find_all('a', class_='ais-details-a product-tile')]
            # all_prices = [price.text.strip() for price in soup.find_all('div', class_='pricing-block')]
            all_links = [f"https://www.jbhifi.com.au{link.get('href')}" for link in soup.find_all('a', class_='ais-details-a product-tile')]
            all_images = [link.get('src') for link in soup.find_all('img', class_='product-tile__image')]
            # all_reviews = [f"{star.find('span', class_='review-rating').text.strip()}/5 out of {star.find('span', class_='review-count').text.strip()} reviews." for star in soup.find_all('div', class_='star-review')]
            #################################################################################################################################################

            browser.close()

            return category_name, all_names, orginal_price, discount_price, customer_reviews, all_links, all_images
