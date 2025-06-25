import re
import hashlib
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def main():
    url = "https://fiaumalta.org/what-we-do/enforcement/administrative/"
    filename = "fiau_admin_feed.xml"

    print("🚀 Fetching FIAU administrative measures page...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 🎯 Select all enforcement titles and dates
    titles = soup.select('a.flex.font-bold.text-base')
    dates = soup.select('div.text-blue-lighter.text-base')

    fg = FeedGenerator()
    fg.id(url)
    fg.title("FIAU Administrative Measures")
    fg.link(href=url, rel="alternate")
    fg.description("Latest enforcement notices published by the FIAU Malta")
    fg.language("en")

    for title_tag, date_tag in zip(titles, dates):
        title = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        full_link = href if href.startswith("http") else "https://fiaumalta.org" + href
        date_text = date_tag.get_text(strip=True)

        try:
            dt = datetime.strptime(date_text, "%d %B %Y")
            pub_date = datetime(dt.year, dt.month, dt.day, 23, 59, 0, tzinfo=timezone.utc)
        except Exception as e:
            print(f"⚠️ Failed to parse date for '{title}': {e}")
            pub_date = datetime.now(timezone.utc)

        guid = hashlib.md5((title + full_link).encode("utf-8")).hexdigest()

        entry = fg.add_entry()
        entry.id(guid)
        entry.guid(guid, permalink=False)
        entry.title(title)
        entry.link(href=full_link)
        entry.pubDate(pub_date)
        entry.updated(pub_date)

        print(f"✅ {title} — {pub_date.date()}")

    fg.rss_file(filename)
    print(f"📄 Feed saved to: {filename}")

if __name__ == "__main__":
    main()
