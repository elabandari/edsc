import requests
from bs4 import BeautifulSoup
import random
import io
import tldextract
from urlextract import URLExtract
from fake_useragent import UserAgent
from string import ascii_uppercase
import time
import json
import psycopg2


class jobbankScraper:
    def scrape_mainpage(self):
        # Get the url
        jobs = []
        for c in ascii_uppercase:
            url = "https://www.jobbank.gc.ca/browsejobs/employer/" + c
            # Pose As a computer
            A = ("Chrome/6.0.472.63 Safari/534.3",)
            # Ignore next line. Not being used right now.
            Agent = A[random.randrange(len(A))]
            # ua = UserAgent()
            # Agent = ua.random
            # Get the website

            headers = {"user-agent": Agent}
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print("Couldn't scrape job bank")
                return -1
            soup = BeautifulSoup(r.text, "lxml")

            # Get the possible website links Case 1
            ll = soup.findAll("a", attrs={"class": "main-element"})
            for l in ll:
                jobs.append((l.text.strip(),))
            time.sleep(5)

        with open("connection.json") as f:
            db = json.load(f)

        conn = psycopg2.connect(
            database=db["dbname"],
            user=db["user"],
            password=db["password"],
            host=db["host"],
        )

        try:
            sql_code = """ DELETE FROM public.jobbank_mainpostings"""
            with conn, conn.cursor() as cur:
                cur.execute(sql_code)
                conn.commit()
            sql_code = (
                """INSERT INTO public.jobbank_mainpostings(business_name) VALUES(%s)"""
            )
            with conn, conn.cursor() as cur:
                cur.executemany(sql_code, jobs)
                conn.commit()
        except Exception as e:
            return -1
        return 0

    def scrape_checkjobposting(self, company_name, location=""):
        try:
            company_name_add = company_name.replace(" ", "+")
            url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?empl="
            url += company_name_add
            url += "&locationstring="
            url += location

            A = ("Chrome/6.0.472.63 Safari/534.3",)
            # Ignore next line. Not being used right now.
            Agent = A[random.randrange(len(A))]
            # ua = UserAgent()
            # Agent = ua.random
            # Get the website

            headers = {"user-agent": Agent}
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print("Couldn't scrape job bank")
                return -1
            soup = BeautifulSoup(r.text, "lxml")
            jobs = []
            # Get the possible website links Case 1
            res = soup.find("span", attrs={"class": "found"})
            return int(res.text)
        except:
            return -1


# gg = jobbankScraper()
# print(gg.scrape_checkjobposting("Boston Pizza"))
# print(gg.scrape_Website_notregistered("dominos"))
# print('-------------')
# print(gg.scrape_Website_registered("dominos"))


# print()

# url = gg.generate_url("Jilaev's Jewellery Ltd")
# A = ("Chrome/6.0.472.63 Safari/534.3",
#     )
# Agent = A[random.randrange(len(A))]
# headers = {'user-agent': Agent}
# r = requests.get(url, headers=headers)
# soup = BeautifulSoup(r.text, 'lxml')
# # ll = soup.findAll('a' , attrs={"class":"VGHMXd"})
# # for l in ll:
# #     print(l['href'])
# #     print("\n")

# tt = soup.prettify()
# with io.open("A.txt", "w", encoding="utf-8") as f:
#     f.write(tt)
# f.close()
# _class='zBAuLc'