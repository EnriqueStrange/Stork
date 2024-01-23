import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread, Event
from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import os

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

def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

def main(search_for, total, stop_event):
    with sync_playwright() as p:
        with open('cities.txt') as f:
            for city in f:
                if stop_event.is_set():
                    break

                print(city)

                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto("https://www.google.com/maps", timeout=60000)

                page.locator('//input[@id="searchboxinput"]').fill(search_for + city)

                page.keyboard.press("Enter")

                page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

                previously_counted = 0
                while True:
                    if stop_event.is_set():
                        break

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

                business_list = BusinessList()

                for listing in listings:
                    try:
                        if stop_event.is_set():
                            break

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
                                .replace(',', '')
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

class GoogleMapsScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Maps Scraper")

        # Set to full screen while maintaining aspect ratio
        self.root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

        self.search_label = ttk.Label(root, text="Search Keyword:")
        self.search_entry = ttk.Entry(root)

        self.total_label = ttk.Label(root, text="Total Listings to Scrape:")
        self.total_entry = ttk.Entry(root)

        self.scrape_button = ttk.Button(root, text="Scrape", command=self.scrape_google_maps)
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_scraping)

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15)

        self.search_label.pack(pady=10)
        self.search_entry.pack(pady=5)
        self.total_label.pack(pady=10)
        self.total_entry.pack(pady=5)
        self.scrape_button.pack(pady=10)
        self.stop_button.pack(pady=5)
        self.output_text.pack(pady=10)

        self.stop_event = Event()

    def scrape_google_maps(self):
        search_query = self.search_entry.get()
        total_listings = int(self.total_entry.get()) if self.total_entry.get() else 1000

        if not search_query:
            messagebox.showinfo("Error", "Please enter a search keyword.")
            return

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Scraping in progress...\n")

        def scrape_thread():
            try:
                self.stop_event.clear()
                main(search_query, total_listings, self.stop_event)
                self.output_text.insert(tk.END, "Scraping completed.\n")
            except Exception as e:
                self.output_text.insert(tk.END, f"Error: {str(e)}\n")

        scraper_thread = Thread(target=scrape_thread)
        scraper_thread.start()

    def stop_scraping(self):
        self.stop_event.set()
        self.output_text.insert(tk.END, "Scraping stopped.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleMapsScraperApp(root)
    root.mainloop()
