from flask import Flask, jsonify
from playwright.sync_api import Playwright, sync_playwright

app = Flask(__name__)

def run_playwright():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://copilot.microsoft.com/")
        page.get_by_placeholder("Ask me anything...").fill("Do these things in serial wise. 1. search for masculinesage twitter account. 2. understand his way of writing tweets. 3. only after you are sure how he thinks, write a tweet in his style. return nothing but the tweet in codeblock. keep in mind the twitter word limit. also use no hashtags.")

        page.get_by_label("Submit").click()
        page.locator("cib-muid-consent").click()
        tweet_data = page.locator("pre").all()[0].inner_text()
        print(tweet_data)
        context.close()
        browser.close()

        return tweet_data

@app.route('/get_tweet', methods=['GET'])
def get_tweet():
    tweet = run_playwright()
    return jsonify({"tweet": tweet})

if __name__ == '__main__':
    app.run(debug=True)
