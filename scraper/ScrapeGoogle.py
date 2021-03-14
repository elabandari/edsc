# Author : Kevin Shahnazari
# Date: March 12th 2021

"""
This script Scrapes the information
from the google website and returns the result 
"""

import requests
from bs4 import BeautifulSoup
import random
import io
import tldextract
from urlextract import URLExtract
from fake_useragent import UserAgent


class GoogleScraper:
    def scrape_Website_registered(self, company_name):
        # Get the url
        url = self.generate_url(company_name)
        # Pose As a computer
        A = ("Chrome/6.0.472.63 Safari/534.3",)
        # Ignore next line. Not being used right now.
        Agent = A[random.randrange(len(A))]
        # Ignore
        # ua = UserAgent()
        # Agent = ua.random

        # Get the website

        headers = {"user-agent": Agent}
        r = requests.get(url, headers=headers)
        # Check if the request got through
        if r.status_code != 200:
            print("Google Detected! Change VPN and MAC")
            return -1
        soup = BeautifulSoup(r.text, "lxml")

        # Get the possible website links Case 1
        ll = soup.findAll("a", attrs={"class": "VGHMXd"})

        # Two links are returned sometimes. We need to delete if one is google maps
        for l in ll:
            # skip maps
            if "maps.google" in l["href"]:
                continue
            # Clean the string for Case 1 and validate if it is a valid url link
            # If valid return
            final_str = self.str_clean1(l["href"])
            if final_str != "" and self.site_online(final_str):
                return final_str

        # Get the possible website links Case 2
        ll = soup.findAll("span", attrs={"class": "r0bn4c rQMQod"})
        if len(ll) != 0:
            final_str = self.str_clean2(ll[0].text)
            # Clean the string for Case 2 and validate if it is a valid url link
            # If valid return
            if final_str != "" and self.site_online(final_str):
                return final_str
        # If nothing is found return none
        return None

    def scrape_Website_notregistered(self, company_name, n=5):
        # Get the url
        url = self.generate_url(company_name)
        # Pose As a computer
        A = ("Chrome/6.0.472.63 Safari/534.3",)
        # Ignore next line. Not being used right now.
        Agent = A[random.randrange(len(A))]

        # Get the website
        headers = {"user-agent": Agent}
        r = requests.get(url, headers=headers)
        # Check if the request got through
        if r.status_code != 200:
            print("Google Detected! Change VPN and MAC")
            return -1
        soup = BeautifulSoup(r.text, "lxml")

        counter = 0
        # Get all URLS shown by the search result
        links = soup.findAll("div", attrs={"class": "BNeawe UPmit AP7Wnd"})

        final_links = []
        for link in links:
            # Clean the string and validate if it is a valid url link.
            # if it is add to the links to return
            final_str = self.str_clean3(link.text)
            if final_str != "" and self.site_online(final_str):
                final_links.append(self.str_clean3(link.text))
            counter += 1
            # If we already scrapped the numbers we had to break
            if counter == n:
                break
        # return results
        return final_links

    def generate_url(self, company_name):
        # Given the company name generate the correct google search url
        company_name_url = company_name.replace(" ", "+")
        return "https://www.google.com/search?q=" + company_name_url

    def str_clean1(self, item):
        extractor = URLExtract()
        if item.startswith("/url?q="):
            if extractor.find_urls(item) != list():
                url = extractor.find_urls(item)[0]
                url = tldextract.extract(url).registered_domain
                return url
        else:
            return ""

    def str_clean2(self, item):
        extractor = URLExtract()
        url = tldextract.extract(item).registered_domain
        return url

    def str_clean3(self, item):
        extractor = URLExtract()
        if extractor.find_urls(item) != list():
            url = extractor.find_urls(item)[0]
            url = tldextract.extract(url).registered_domain
            return url
        else:
            return ""

    def site_online(self, url):
        # Checks if a url is valid by sending a request
        try:
            ret = requests.head(f"http://www.{url}")
            return True
        except:
            return False