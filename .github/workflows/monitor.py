import feedparser
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os

RSS_FEED = os.environ.get("RSS_FEED")
YOUTUBE_CHANNEL_URL = os.environ.get("YOUTUBE_CHANNEL_URL")

TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")


def send_email():
    msg = MIMEText("No podcast upload as of 17:30.")
    msg["Subject"] = "Podcast Not uploaded"
    msg["From"] = SENDER_EMAIL
    msg["To"] = TARGET_EMAIL

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


def check_rss():
    feed = feedparser.parse(RSS_FEED)
    if not feed.entries:
        return False

    latest = feed.entries[0]
    published = datetime(*latest.published_parsed[:6])

    return published.date() == datetime.now().date()


def check_youtube():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(YOUTUBE_CHANNEL_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text()

    if "hour ago" in text or "minutes ago" in text:
        return True

    return False


def main():
    now = datetime.now()

    # Only run after 17:30
    if now.hour < 17 or (now.hour == 17 and now.minute < 30):
        return

    if not (check_rss() and check_youtube()):
        send_email()


if __name__ == "__main__":
    main()
