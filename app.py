import customtkinter as ctk
from tkinter import filedialog
from Scraper.scraper_module import scrape_google_maps_data
import threading

class Stork(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.stop_flag = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        self.geometry("500x700")
        self.title("Stork")
        ctk.set_appearance_mode("system")
        self.configure(fg_color=("#d1dadb", "#262833"))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_window_close)  # Bind window close event

        self.tab = ctk.CTkTabview(master=self, fg_color=("#84b898", "#4b4c56"), width=400, height=600)
        self.tab.pack(padx=20, pady=20)

        self.tab.add("Scraper")
        self.tab.add("Texter")
        self.tab.add("Editor")

        self.keywordBox = ctk.CTkEntry(master=self.tab.tab("Scraper"), placeholder_text="Enter Keyword", width=300,
                                       fg_color="transparent", text_color=("#3a3d46", "#a6a7ac"),
                                       placeholder_text_color=("#3a3d46", "#a6a7ac"))
        self.keywordBox.place(relx=0.5, rely=0.15, anchor="center")

        self.listCount = ctk.CTkEntry(master=self.tab.tab("Scraper"), placeholder_text="Total Listing to Scrape", width=300,
                                      fg_color="transparent", text_color=("#3a3d46", "#a6a7ac"))
        self.listCount.place(relx=0.5, rely=0.22, anchor="center")

        self.locationoutput = ctk.CTkTextbox(master=self.tab.tab("Scraper"), width=150, height=5,
                                             fg_color=("#d1dadb", "#262833"))
        self.locationoutput.place(relx=0.305, rely=0.28, anchor="center")

        self.locFile = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Select Location file", fg_color="transparent",
                                     hover_color=("#84b898", "#84b898"), text_color=("#e5ede8"), border_color="#e5ede8",
                                     border_width=1, command=lambda: self.get_file_name())
        self.locFile.place(relx=0.7, rely=0.28, anchor="center")

        self.scrapeBtn = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Scrape", fg_color=("#e5ede8", "#e5ede8"),
                                       hover_color=("#84b898", "#84b898"), text_color=("#1d1f2b"), command=self.start_scraping)
        self.scrapeBtn.place(relx=0.305, rely=0.38, anchor="center")

        self.stopscrapeBtn = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Stop", fg_color=("#e5ede8", "#e5ede8"),
                                           hover_color=("#84b898", "#84b898"), text_color=("#1d1f2b"),
                                           command=self.stop_scraping)
        self.stopscrapeBtn.place(relx=0.685, rely=0.38, anchor="center")

        self.scraperOp = ctk.CTkTextbox(master=self.tab.tab("Scraper"), width=350, corner_radius=15,
                                        fg_color=("#d1dadb", "#262833"), padx=10, pady=10)
        self.scraperOp.place(relx=0.5, rely=0.72, anchor="center")
        self.scraperOp.insert("0.0", ">>\n")

        self.downloadCSV = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Download txt", fg_color=("#e5ede8", "#e5ede8"),
                                       hover_color=("#84b898", "#84b898"), text_color=("#1d1f2b"), command=self.start_scraping)
        self.downloadCSV.place(relx=0.5, rely=0.91, anchor="center")


    def on_window_close(self):
        self.stop_flag.set()  # Set the stop flag when the window is closed
        self.destroy()

    def get_file_name(self):
        try:
            filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                                  filetypes=(("Text files", "*.txt*"), ("all files", "*.*")))
            self.locationoutput.insert("0.0", text=filename)
        except Exception as e:
            self.display_error(f"Error while getting file name: {e}")

    def start_scraping(self):
        try:
            self.scrapeBtn.configure(state="disabled")
            self.stop_flag.clear()
            threading.Thread(target=self.scrape_and_display).start()
        except Exception as e:
            self.display_error(f"Error while starting scraping: {e}")

    def stop_scraping(self):
        try:
            self.stop_flag.set()
        except Exception as e:
            self.display_error(f"Error while stopping scraping: {e}")

    def get_keyword(self):
        return self.keywordBox.get()

    def get_listcount(self):
        return int(self.listCount.get())

    def get_file_location_for_cities(self):
        return self.locationoutput.get(0.1, ctk.END)

    def display_error(self, error_message):
        self.scraperOp.insert("0.0", f"Error: {error_message}\n")

    def scrape_and_display(self):
        try:
            keyword = self.get_keyword()
            total_listings = self.get_listcount()
            cities_file_path = self.get_file_location_for_cities()

            scraped_data = scrape_google_maps_data(keyword, total_listings, cities_file_path, self.stop_flag, self.update_scraper_op)

            if scraped_data:
                self.scraperOp.delete("0.0", ctk.END)
                self.scraperOp.insert("0.0", scraped_data.dataframe().to_string(index=False))
        except Exception as e:
            self.display_error(f"Error during scraping: {e}")
        finally:
            self.scrapeBtn.configure(state="normal")

    def update_scraper_op(self, data):
        self.scraperOp.insert("0.0", f"{data}\n")


if __name__ == "__main__":
    app = Stork()
    app.mainloop()
