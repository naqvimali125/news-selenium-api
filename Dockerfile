FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Chrome browser and matching ChromeDriver
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget curl unzip jq ca-certificates fonts-liberation \
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb \
    && MAJOR=$(google-chrome --version | grep -oE '[0-9]+' | head -1) \
    && URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json | jq -r ".milestones[\"$MAJOR\"].downloads.chromedriver[] | select(.platform==\"linux64\") | .url") \
    && test -n "$URL" \
    && wget -q -O /tmp/chromedriver.zip "$URL" \
    && unzip -q /tmp/chromedriver.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chrome.deb /tmp/chromedriver.zip /tmp/chromedriver-linux64 /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py scraper.py summarizer.py ./

EXPOSE 7000

# The API starts automatically when the container runs
CMD ["gunicorn", "-w", "1", "--threads", "2", "-t", "180", "-b", "0.0.0.0:7000", "app:app"]
