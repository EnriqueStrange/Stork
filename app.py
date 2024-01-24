import customtkinter as ctk
from tkinter import filedialog
from Scraper.scraper_module import scrape_google_maps_data


class Stork(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry()
        self.title("Stork")
        ctk.set_appearance_mode("system")
        self.configure(fg_color=("#d1dadb", "#262833"))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tab = ctk.CTkTabview(master=self, fg_color=("#84b898","#4b4c56"), width=400, height=600)
        self.tab.pack(padx=20, pady=20)

        self.tab.add("Scraper")
        self.tab.add("Texter")
        self.tab.add("Editor")

        def get_keyword():
            keyword = (self.keywordBox.get())
            return keyword
        self.get_keyword = get_keyword

        def get_listcount():
            listcount = (self.listCount.get())
            return int(listcount)
        self.get_listcount = get_listcount

        def get_file_name():
            filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("Text files", "*.txt*"), ("all files", "*.*")))
            self.locationoutput.insert("0.0", text=filename)
        self.get_file_name = get_file_name

        def get_file_location_for_cities():
            location_for_cities = self.locationoutput.get(0.1, ctk.END)
            return(location_for_cities)

        self.get_file_name = get_file_name
            
        def scrape_and_display():
            keyword = get_keyword()
            print(keyword)
            total_listings = get_listcount()
            print(total_listings)
            cities_file_path = get_file_location_for_cities() # Assuming this is the file path selected by the user
            print(cities_file_path)

            scraped_data = scrape_google_maps_data(keyword, total_listings, cities_file_path)
            self.scraperOp.delete("0.0", ctk.END)
            self.scraperOp.insert("0.0", scraped_data.dataframe().to_string(index=False))

        self.scrape_and_display = scrape_and_display

        self.keywordBox = ctk.CTkEntry(master=self.tab.tab("Scraper"), placeholder_text="Enter Keyword", width=300,
                                       fg_color="transparent", text_color=("#3a3d46","#a6a7ac"),
                                       placeholder_text_color=("#3a3d46","#a6a7ac"))
        self.keywordBox.place(relx=0.5, rely=0.15, anchor="center")

        self.listCount = ctk.CTkEntry(master=self.tab.tab("Scraper"), placeholder_text="Total Listing to Scrape", width=300,
                                      fg_color="transparent", text_color=("#3a3d46","#a6a7ac"))
        
        self.listCount.place(relx=0.5, rely=0.22, anchor="center")

        self.locationoutput = ctk.CTkTextbox(master=self.tab.tab("Scraper"), width=150, height=5,
                                        fg_color=("#d1dadb", "#262833"))
        
        self.locationoutput.place(relx=0.305, rely=0.28, anchor="center")

        self.locFile = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Select Location file", fg_color="transparent", hover_color=("#84b898","#84b898"), text_color=("#e5ede8"), border_color= "#e5ede8", border_width=1, command=lambda: self.get_file_name())
        self.locFile.place(relx=0.7, rely=0.28, anchor="center")

        self.scrapeBtn = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Scrape", fg_color=("#e5ede8", "#e5ede8"),
                                       hover_color=("#84b898","#84b898"), text_color=("#1d1f2b"), command=self.scrape_and_display) # command=self.scrape_and_display
        self.scrapeBtn.place(relx=0.305, rely=0.38, anchor="center")

        self.stopscrapeBtn = ctk.CTkButton(master=self.tab.tab("Scraper"), text="Stop", fg_color=("#e5ede8", "#e5ede8"),
                                           hover_color=("#84b898","#84b898"), text_color=("#1d1f2b"))
        self.stopscrapeBtn.place(relx=0.685, rely=0.38, anchor="center")

        self.scraperOp = ctk.CTkTextbox(master=self.tab.tab("Scraper"), width=350, corner_radius=15,
                                        fg_color=("#d1dadb", "#262833"), padx=10, pady=10)
        self.scraperOp.place(relx=0.5, rely=0.72, anchor="center")
        self.scraperOp.insert("0.0", ">>\n")



if __name__ == "__main__":
    app = Stork()
    app.geometry("500x700")
    app.minsize(500, 700)
    app.maxsize(500, 700)
    app.mainloop()
