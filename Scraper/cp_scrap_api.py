from flask import Flask, jsonify, request
from playwright.sync_api import Playwright, sync_playwright

app = Flask(__name__)

def run_playwright(search_query):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://copilot.microsoft.com/")
        page.get_by_placeholder("Ask me anything...").fill(search_query + " Return teh response in the codeblock. ")
        page.get_by_label("Submit").click()
        page.locator("cib-muid-consent").click()
        tweet_data = page.locator("pre").all()[0].inner_text()
        print(tweet_data)
        context.close()
        browser.close()

        return tweet_data

@app.route('/get_tweet', methods=['POST'])
def get_tweet():
    try:
        data = request.get_json()
        search_query = data['search_query']
        tweet = run_playwright(search_query)
        return jsonify({"tweet": tweet})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
