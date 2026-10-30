import threading

from flask import Flask, jsonify, request

from scraper import article_text, first_result, make_driver
from summarizer import summarize

REG = "SP23-BAI-048"
SOURCE = "Al Jazeera Media Network"

app = Flask(__name__)
app.json.sort_keys = False
lock = threading.Lock()

HOME = """<!doctype html>
<html><head><title>News Summary API</title></head>
<body style="font-family: Arial, sans-serif; max-width: 640px; margin: 40px auto;">
<h1>News Summary API</h1>
<p><b>Registration number:</b> __REG__</p>
<p><b>News source:</b> __SRC__</p>
<p>Use: <code>/get?keyword=pakistan</code></p>
<form action="/get" method="get">
<input name="keyword" placeholder="keyword" required>
<button type="submit">Search</button>
</form>
</body></html>"""


def payload(keyword, url="", summary=""):
    return {"registration": REG, "newssource": SOURCE, "keyword": keyword, "url": url, "summary": summary}


@app.route("/")
def home():
    return HOME.replace("__REG__", REG).replace("__SRC__", SOURCE)


@app.route("/health")
def health():
    return jsonify({"registration": REG, "status": "ok"})


@app.route("/get")
def get():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return jsonify(payload("", "", "keyword query parameter is required")), 400
    with lock:
        driver = None
        try:
            driver = make_driver()
            url = first_result(driver, keyword)
            if not url:
                return jsonify(payload(keyword, "", "No search result found")), 404
            title, text = article_text(driver, url)
            return jsonify(payload(keyword, url, summarize(text, title)))
        except Exception as exc:
            return jsonify(payload(keyword, "", "error: " + str(exc)[:200])), 502
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
