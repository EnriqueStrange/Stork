from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import os

app = Flask(__name__)

@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None

@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)

    def dataframe(self):
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

    def save_to_excel(self, filename):
        file_path = f"{filename}.xlsx"
        if os.path.exists(file_path):
            existing_data = pd.read_excel(file_path)
            updated_data = pd.concat([existing_data, self.dataframe()], ignore_index=True)
            updated_data.to_excel(file_path, index=False)
        else:
            self.dataframe().to_excel(file_path, index=False)

    def save_to_csv(self, filename):
        file_path = f"{filename}.csv"
        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            updated_data = pd.concat([existing_data, self.dataframe()], ignore_index=True)
            updated_data.to_csv(file_path, index=False)
        else:
            self.dataframe().to_csv(file_path, index=False)

def extract_coordinates_from_url(url: str) -> tuple[float,float]:
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

@app.route('/scrape', methods=['POST'])
def scrape_google_maps():
    data = request.get_json()

    search_for = data.get('search', 'Coaching')
    total = data.get('total', 1000)

    business_list = BusinessList()

    with sync_playwright() as p:
        with open('cities.txt') as f:
            for city in f:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://www.google.com/maps", timeout=60000)
                page.locator('//input[@id="searchboxinput"]').fill(search_for + city)
                page.keyboard.press("Enter")

                previously_counted = 0
                while True:
                    page.mouse.wheel(0, 10000)
                    page.wait_for_timeout(3000)

                    if (
                        page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).count()
                        >= total
                    ):
                        listings = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).all()[:total]
                        listings = [listing.locator("xpath=..") for listing in listings]
                        print(f"Total Scraped: {len(listings)}")
                        break
                    else:
                        if (
                            page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count()
                            == previously_counted
                        ):
                            listings = page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).all()
                            print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                            break
                        else:
                            previously_counted = page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count()
                            print(
                                f"Currently Scraped: ",
                                page.locator(
                                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                                ).count(),
                            )

                for listing in listings:
                    try:
                        listing.click()
                        page.wait_for_timeout(5000)
                        
                        name_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]'
                        address_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[3]/button/div/div[2]/div[1]'
                        website_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[5]/a/div/div[2]/div[1]'
                        phone_number_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[7]/button/div'
                        reviews_span_xpath = 'Add xpath '

                        business = Business()

                        if listing.locator(name_xpath).count() > 0:
                            business.name = listing.locator(name_xpath).all()[0].inner_text()
                        else:
                            business.name = ""
                        if page.locator(address_xpath).count() > 0:
                            business.address = page.locator(address_xpath).all()[0].inner_text()
                        else:
                            business.address = ""
                        if page.locator(website_xpath).count() > 0:
                            business.website = page.locator(website_xpath).all()[0].inner_text()
                        else:
                            business.website = ""
                        if page.locator(phone_number_xpath).count() > 0:
                            business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                        else:
                            business.phone_number = ""
                        if listing.locator(reviews_span_xpath).count() > 0:
                            business.reviews_average = float(
                                listing.locator(reviews_span_xpath).all()[0]
                                .get_attribute("aria-label")
                                .split()[0]
                                .replace(",", ".")
                                .strip()
                            )
                            business.reviews_count = int(
                                listing.locator(reviews_span_xpath).all()[0]
                                .get_attribute("aria-label")
                                .split()[2]
                                .replace(',','')
                                .strip()
                            )
                        else:
                            business.reviews_average = ""
                            business.reviews_count = ""
                        
                        business.latitude, business.longitude = extract_coordinates_from_url(page.url)

                        business_list.business_list.append(business)
                    except Exception as e:
                        print(e)

                business_list.save_to_excel("google_maps_data")
                business_list.save_to_csv("google_maps_data")

                browser.close()
                if 'str' in city:
                    break

    return jsonify({'message': 'Scraping completed successfully!', 'data': asdict(business_list)})

if __name__ == "__main__":
    app.run(debug=True)
