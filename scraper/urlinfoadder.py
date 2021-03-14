from Scrapewhois import WhoisScraper
import psycopg2
import json
import datetime
import time
from random import randint


def add_one_url_info():
    with open("connection.json") as f:
        db = json.load(f)

    conn = psycopg2.connect(
        database=db["dbname"], user=db["user"], password=db["password"], host=db["host"]
    )

    # try:
    if randint(0, 1):
        with conn, conn.cursor() as cur:
            cur.execute(
                """SELECT registered_urls.url
            FROM public.registered_urls  
            LEFT JOIN public.url_info ON registered_urls.url = url_info.url
            WHERE url_info.url IS NULL AND registered_urls.url IS NOT NULL ORDER BY RANDOM() LIMIT 1"""
            )
            for company_url in cur.fetchall():
                company_url_scrape = company_url[0]
    else:
        with conn, conn.cursor() as cur:
            cur.execute(
                """SELECT possible_urls.url
            FROM public.possible_urls
            LEFT JOIN public.url_info ON possible_urls.url = url_info.url
            WHERE url_info.url IS NULL AND possible_urls.url IS NOT NULL ORDER BY RANDOM() LIMIT 1"""
            )
            for company_url in cur.fetchall():
                company_url_scrape = company_url[0]

    gg = WhoisScraper()
    url = gg.scrape(company_url_scrape)
    # Meaning We scraped correctly
    if url != -1:
        events = url[0]
        sql_code = """ INSERT INTO public.url_info(url,register_date,expire_date,last_update_date,json_info)
        VALUES(%s,%s,%s,%s,%s)"""
        with conn, conn.cursor() as cur:
            url_data = str(url[1])
            cur.execute(
                sql_code,
                (
                    company_url,
                    events["register_date"],
                    events["expire_date"],
                    events["last_update_date"],
                    url_data,
                ),
            )
            conn.commit()
            print(f"Added Company Name {company_url} URL info")
    else:
        print(f"Failed to get {company_url} info")

    # except Exception as e:
    #     print("Error in urladder.")
    #     print(e)


# add_one_url_info()
