import pandas as pd
import threading
from playwright.sync_api import sync_playwright

def texter(numbers):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto("https://web.whatsapp.com/", timeout=60000)

            with open(numbers.strip()) as f:
                for number in f:
                    # if stop_flag.is_set():
                    #     break

                    print(number)

                    

    except Exception as e:
        print(f"Error during scraping: {e}")
        return None

texter('numbers.txt')