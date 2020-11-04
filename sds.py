import os
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chrome_options


class BrowserChrome:
    path = "\driver\chromedriver.exe"
    extensions = []
    homepage = "data:,"

    def __init__(self, path=path, extensions=extensions, homepage=homepage):
        driver_path = os.getcwd() + path
        options = self.get_options(extensions, homepage)
        self.driver = webdriver.Chrome(executable_path=driver_path, options=options)

    def get_driver(self):
        return self.driver

    def get_options(self, extensions, url):
        options = chrome_options()
        options.add_argument("--start-maximized")
        options.add_argument("--homepage {}".format(url))
        # options.headless = True # disabled because some different behaviours detected from web site
        for extension in extensions:
            options.add_extension(os.getcwd() + extension)
        return options


class MarketSok:
    base_url = "https://www.sokmarket.com.tr/"

    def __init__(self):
        self.browser = BrowserChrome(homepage=self.base_url, extensions=['\driver\Block-image_v1.1.crx']).get_driver()
        self.products = []

    def get_categories(self):
        categories = {}
        page_content = BeautifulSoup(self.browser.page_source, 'lxml')

        while page_content.find("ul", "categories-list") is None:
            page_content = BeautifulSoup(self.browser.page_source, 'lxml')
        try:
            for category in page_content.find("ul", "categories-list").find_all("li", "list-category"):
                url = urljoin(self.base_url, category.find("a")['href'])
                categories[category.find("h3").text.strip()] = url
            # print(categories)
        except Exception as e:
            print('get_categories', e)
            raise
        return categories

    def get_sub_categories(self):
        sub_categories = {}
        page_content = BeautifulSoup(self.browser.page_source, 'lxml')

        while page_content.find("h1", "head-title") is None:
            page_content = BeautifulSoup(self.browser.page_source, 'lxml')

        try:
            if len(page_content.find("div", "listing-head").find_all("div")) > 1:
                for sub_category in page_content.find("nav", "nav-list").find_all("li", "list-item"):
                    url = urljoin(self.base_url, sub_category.find("a")['href'])
                    sub_categories[sub_category.find("a").text.strip()] = url
            else:
                sub_categories[page_content.find("h1", "head-title").text.strip()] = self.browser.current_url
            # print(sub_categories)
        except Exception as e:
            print('get_sub_categories', e)
            raise
        return sub_categories

    def get_campaigns(self):
        pass

    def get_products(self):
        page_content = BeautifulSoup(self.browser.page_source, 'lxml')

        while page_content.find("div", "pricetag") is None:
            page_content = BeautifulSoup(self.browser.page_source, 'lxml')

        try:
            for product in page_content.find("ul", "results-list").find_all("li", "list-item"):
                product_name = product.find("strong", "content-title").text.strip()
                product_url = urljoin(self.base_url, product.find("a")['href'])
                product_price = product.find("div", "pricetag").find_all("span")[-1].text \
                    .replace(".", "").replace(",", ".").strip()
                print(product_name, product_price, product_url)
                self.products.append({"name": product_name, "price": product_price, "url": product_url})

        except Exception as e:
            print('get_products', e)
            raise

    def get_all_products(self):
        try:
            for category, category_url in self.get_categories().items():
                self.browser.get(category_url)
                for sub_category, sub_category_url in self.get_sub_categories().items():
                    if self.browser.current_url != sub_category_url:
                        self.browser.get(sub_category_url)
                    self.get_products()
        except Exception as e:
            print('get_all_products', e)
            raise
        return self.products

    def get_product_detail(self):
        pass

    def done(self):
        self.browser.quit()


if __name__ == "__main__":
    market_sok = MarketSok()
    products = market_sok.get_all_products()
    market_sok.done()
