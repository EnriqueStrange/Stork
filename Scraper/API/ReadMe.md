# Google Maps Scraper API

This API allows you to scrape data from Google Maps for businesses based on a specified search query and total number of results.

## Getting Started

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/google-maps-scraper-api.git
   ```

2. Navigate to the project directory:

   ```bash
   cd google-maps-scraper-api
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the API

Execute the following command to start the API:

```bash
python google_maps_scraper.py
```

The API will be accessible at `http://127.0.0.1:5000`.

## Endpoints

### Scrape Google Maps

- **Endpoint:** `/scrape`
- **Method:** POST
- **Payload:**

  ```json
  {
    "search": "Coaching",
    "total": 1000
  }
  ```

  - `search` (optional): The search query to use on Google Maps. Default is "Coaching".
  - `total` (optional): The total number of results to scrape. Default is 1000.

- **Example Usage:**

  ```python
  import requests

  url = "http://127.0.0.1:5000/scrape"
  data = {"search": "Restaurants", "total": 500}
  response = requests.post(url, json=data)

  print(response.json())
  ```

## Notes

- Ensure that you have Playwright and other dependencies installed before running the API.

- This is a basic example, and in a production environment, additional considerations such as security, error handling, and deployment using a production-ready web server should be addressed.

- Respect the terms of service of websites, including Google Maps, when using this API.

```
