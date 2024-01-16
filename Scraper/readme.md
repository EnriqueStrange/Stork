**Document Title: Google Maps Business Scraper v1 Documentation**

### Objective:

The objective of this Python script is to scrape business information from Google Maps based on user-defined search queries and locations. The script utilizes the Playwright library to automate interactions with the Google Maps web interface, extract data, and organize it into a structured format. The primary goal is to provide users with a convenient way to gather business details, such as name, address, website, and phone number, for further analysis or storage.

### Requirements:

1. **Command-Line Arguments:**
   - `-s` or `--search`: Specify the search term for Google Maps (e.g., "dentist").
   - `-l` or `--location`: Specify the location for the search (e.g., "new york").

   If these arguments are not provided, the script defaults to searching for "dentist new york."

2. **Web Scraping:**
   - Use Playwright to automate the browser for interacting with Google Maps.
   - Perform a search based on the user-provided search term and location.
   - Extract business information from the search results, including name, address, website, and phone number.

3. **Data Structuring:**
   - Define two data classes (`Business` and `BusinessList`) to structure the scraped data.
   - Use these classes to create a Pandas DataFrame for easy manipulation and analysis of the data.

4. **Data Output:**
   - Save the extracted business data to both Excel (.xlsx) and CSV (.csv) files.
   - Files are named based on the search term (e.g., "google_map_data.xlsx" and "google_map_data.csv").

### Approach:

1. **Initialization:**
   - Initialize Playwright and launch a Chromium browser.

2. **Search Execution:**
   - Navigate to Google Maps and perform a search based on the user-defined search term and location.
   - Handle user-provided or default search parameters.

3. **Scraping Business Information:**
   - Locate and extract relevant information from the search results, including business name, address, website, and phone number.
   - Utilize XPath expressions to target specific elements on the page.

4. **Data Structuring:**
   - Organize the scraped data into instances of the `Business` class and store them in a `BusinessList` object.

5. **Data Output:**
   - Convert the data to a Pandas DataFrame for easy manipulation.
   - Save the data to Excel and CSV files using the provided methods in the `BusinessList` class.

6. **Closing Browser:**
   - Close the browser instance after scraping and saving the data.

### Tech Stack:

- **Programming Language:** Python
- **Web Automation Library:** Playwright
- **Data Manipulation Library:** Pandas

### Usage:

The script is intended to be executed from the command line, accepting user-provided search and location parameters. Example usage:

```bash
python main.py -s "restaurant" -l "san francisco"
```

If no search term and location are provided, the script defaults to:

```bash
python main.py
```

### Conclusion:

This script provides a straightforward and automated solution for scraping business information from Google Maps, empowering users to gather relevant data for diverse applications, such as market research, lead generation, or business analysis. Users can tailor the search parameters based on their specific requirements.