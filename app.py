import customtkinter as ctk
from tkinter import Entry, filedialog
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

class Stork(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry()
        self.title("Stork")
        ctk.set_appearance_mode("system")
        self.configure(fg_color=("#d1dadb", "#262833")) 
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        self.tab = ctk.CTkTabview(master=self, fg_color=("#84b898","#4b4c56"), width=400, height=600)
        self.tab.pack(padx=20, pady=20)

        self.tab.add("Scraper")
        self.tab.add("Texter")
        self.tab.add("Editor")

        def get_file_name():
            filename = filedialog.askopenfilename(initialdir = "/",
                                                title = "Select a File",
                                                filetypes = (("Text files",
                                                                "*.txt*"),
                                                            ("all files",
                                                                "*.*")))

        
        self.keywordBox = ctk.CTkEntry(master=self.tab.tab("Scraper"), placeholder_text="Enter Keyword", width=300, fg_color="transparent", text_color=("#3a3d46","#a6a7ac"), placeholder_text_color=("#3a3d46","#a6a7ac"))
        self.keywordBox.place(relx=0.5, rely=0.15, anchor="center")

        self.listCount = ctk.CTkEntry(master=self.tab.tab("Scraper"), placeholder_text="Total listing to scrape", width=300, fg_color="transparent", text_color=("#3a3d46","#a6a7ac"), placeholder_text_color=("#3a3d46","#a6a7ac"))
        self.listCount.place(relx=0.5, rely=0.22, anchor="center")

        self.locFile = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Select Location file", fg_color="transparent", hover_color=("#84b898","#84b898"), text_color=("#e5ede8"), border_color= "#e5ede8", border_width=1 , command=lambda: get_file_name())
        self.locFile.place(relx=0.5, rely=0.28, anchor="center")


        self.scrapeBtn = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Scrape", fg_color=("#e5ede8", "#e5ede8"), hover_color=("#84b898","#84b898"), text_color=("#1d1f2b"))
        self.scrapeBtn.place(relx=0.305, rely=0.38, anchor="center")

        self.stopscrapeBtn = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Stop", fg_color=("#e5ede8", "#e5ede8"), hover_color=("#84b898","#84b898"), text_color=("#1d1f2b"))
        self.stopscrapeBtn.place(relx=0.685, rely=0.38, anchor="center")

        self.scraperOp = ctk.CTkTextbox(master=self.tab.tab("Scraper"), width=350, corner_radius=15, fg_color=("#d1dadb", "#262833"), padx=10, pady=10)
        self.scraperOp.place(relx=0.5, rely=0.72, anchor="center")
        self.scraperOp.insert("0.0", "Some example text!\n")

        def button_click():
            print("pressed")

        

if __name__ == "__main__":
    app = Stork()
    app.geometry("500x700")
    # set minimum window size value
    app.minsize(500, 700)
    
    # set maximum window size value
    app.maxsize(500, 700)
    app.mainloop()
