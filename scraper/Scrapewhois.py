import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import random
import io


class WhoisScraper:
    def scrape(self, website_url):
        # The request Url
        urls_to_try = []
        urls_to_try.append("https://rdap.markmonitor.com/rdap/domain/" + website_url)
        urls_to_try.append("https://rdap.verisign.com/com/v1/domain/" + website_url)
        urls_to_try.append(
            "https://rdap.publicinterestregistry.net/rdap/org/domain/" + website_url
        )
        urls_to_try.append("https://rdap.ca.fury.ca/rdap/domain/" + website_url)
        urls_to_try.append(
            "https://rdap.registrar.amazon.com/rdap/domain/" + website_url
        )
        # Return important dates and raw json file
        for url in urls_to_try:
            try:
                r = requests.get(url)
                r = r.json()
                time_status = {}
                r_events = r["events"]
                for event in r_events:
                    date_raw = event["eventDate"]
                    # The first 10 characters contain the date
                    date_clean = datetime.strptime(date_raw[0:10], "%Y-%m-%d").date()
                    if event["eventAction"] == "registration":
                        time_status["register_date"] = date_clean
                    if event["eventAction"] == "expiration":
                        time_status["expire_date"] = date_clean
                    if event["eventAction"] == "last update":
                        time_status["last_update_date"] = date_clean
                if "register_date" not in time_status:
                    time_status["register_date"] = None
                if "expire_date" not in time_status:
                    time_status["expire_date"] = None
                if "last_update_date" not in time_status:
                    time_status["last_update_date"] = None
                return time_status, r
            except:
                pass
        return -1


# whos = WhoisScraper()
# print(whos.scrape("amazon.com"))
