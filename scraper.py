import re
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE = "https://www.aljazeera.com"
ARTICLE_RE = re.compile(r"^https://www\.aljazeera\.com/[a-z\-]+/\d{4}/\d{1,2}/\d{1,2}/[^/?#]+")
SELECTORS = [
    ".search-result a[href]",
    "section.search-results a[href]",
    "article.gc a.u-clickable-card__link",
    "a.u-clickable-card__link",
    "main a[href]",
    "a[href]",
]


def make_driver():
    opts = Options()
    opts.binary_location = "/usr/bin/google-chrome"
    for arg in [
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1366,900",
        "--lang=en-US",
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    ]:
        opts.add_argument(arg)
    opts.page_load_strategy = "eager"
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=opts)
    driver.set_page_load_timeout(45)
    return driver


def _is_article(href):
    return bool(href) and bool(ARTICLE_RE.match(href))


def first_result(driver, keyword):
    driver.get(f"{BASE}/search/{quote(keyword)}")

    def has_links(d):
        return any(_is_article(a.get_attribute("href")) for a in d.find_elements(By.CSS_SELECTOR, "a[href]"))

    try:
        WebDriverWait(driver, 25).until(has_links)
    except TimeoutException:
        return None
    for sel in SELECTORS:
        for a in driver.find_elements(By.CSS_SELECTOR, sel):
            href = a.get_attribute("href")
            if _is_article(href):
                return href.split("?")[0]
    return None


def article_text(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 25).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "main p")) > 2)
    except TimeoutException:
        pass
    title = ""
    heads = driver.find_elements(By.CSS_SELECTOR, "h1")
    if heads:
        title = heads[0].text.strip()
    paras = [p.text.strip() for p in driver.find_elements(By.CSS_SELECTOR, "main p")]
    paras = [t for t in paras if len(t) > 40]
    return title, " ".join(paras)
