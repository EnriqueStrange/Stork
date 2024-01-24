from dataclasses import dataclass, asdict, field
import pandas as pd
import threading
from playwright.sync_api import sync_playwright

@dataclass
class Business:
    phone_number: str = None

@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)

    def text_representation(self):
        result = ""
        for business in self.business_list:
            result += f"{business.phone_number}\n\n"
        return result.strip()

stop_flag = threading.Event()

def stop_scraping():
    stop_flag.set()

def reset_stop_flag():
    stop_flag.clear()

def scrape_google_maps_data(keyword, total_listings, cities_file_path, stop_flag, update_callback):
    try:
        with sync_playwright() as p:
            with open(cities_file_path.strip()) as f:
                for city in f:
                    if stop_flag.is_set():
                        break

                    print(city)

                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()

                    page.goto("https://www.google.com/maps", timeout=60000)
                    page.locator('//input[@id="searchboxinput"]').fill(keyword + city)
                    page.keyboard.press("Enter")
                    page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

                    previously_counted = 0
                    while True:
                        if stop_flag.is_set():
                            break

                        page.mouse.wheel(0, 10000)
                        page.wait_for_timeout(3000)

                        if (
                            page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count()
                            >= total_listings
                        ):
                            listings = page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).all()[:total_listings]
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

                    business_list = BusinessList()

                    for idx, listing in enumerate(listings, start=1):
                        if stop_flag.is_set():
                            break

                        try:
                            listing.click()
                            page.wait_for_timeout(5000)

                            phone_number_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[7]/button/div'

                            business = Business()

                            if page.locator(phone_number_xpath).count() > 0:
                                business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                                business_list.business_list.append(business)

                                # Update UI with the scraped data
                                update_callback(business_list.text_representation())

                        except Exception as e:
                            print(e)

                    browser.close()
                    if 'str' in city:
                        break

        return business_list

    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
