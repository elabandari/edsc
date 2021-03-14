from ScrapeGoogle import GoogleScraper
import psycopg2
import json
import datetime
import time
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 

def add_one_url_registered():
    with open('connection.json') as f:
        db = json.load(f)

    conn = psycopg2.connect(database=db['dbname'], user=db['user'], password=db['password'], host=db['host'])

    try:
        with conn, conn.cursor() as cur:
            cur.execute("""SELECT id_mapping.businessname
            FROM public.id_mapping
            LEFT JOIN public.registered_urls ON registered_urls.businessname = id_mapping.businessname
            WHERE registered_urls.businessname IS NULL ORDER BY RANDOM() LIMIT 1""")
            for company_name in cur.fetchall():
                company_name_scrape = company_name[0]

        gg = GoogleScraper()
        url = gg.scrape_Website_registered(company_name_scrape)
        # Meaning We scraped correctly
        if url != -1:
            sql_code = """ INSERT INTO public.registered_urls(businessname,url,date_added)
            VALUES(%s,%s,%s)"""
            with conn, conn.cursor() as cur:
                cur.execute(sql_code,(company_name,url,datetime.datetime.now()))
                conn.commit()
            if url is not None:
                print(f"Added Company Name {company_name} with url {url}")
            else:
                print(f"Added Company Name {company_name} with url None")
            
        time.sleep(5)

    except Exception as e:
        print("Error in urladder.")
        print(e)


def add_one_url_predicted():
    with open('connection.json') as f:
        db = json.load(f)

    conn = psycopg2.connect(database=db['dbname'], user=db['user'], password=db['password'], host=db['host'])

    try:
        with conn, conn.cursor() as cur:
            cur.execute("""SELECT registered_urls.businessname
            FROM public.registered_urls
            LEFT JOIN public.possible_urls ON registered_urls.businessname = possible_urls.businessname
            WHERE registered_urls.url IS NULL AND possible_urls.businessname IS NULL ORDER BY RANDOM() LIMIT 1""")
            for company_name in cur.fetchall():
                company_name_scrape = company_name[0]

        gg = GoogleScraper()
        links = gg.scrape_Website_notregistered(company_name_scrape)
        # Meaning We scraped correctly
        if links != -1:
            link, prob = process.extractOne(company_name_scrape, links)
            sql_code = """ INSERT INTO public.possible_urls(businessname,url,prob)
            VALUES(%s,%s,%s)"""
            with conn, conn.cursor() as cur:
                cur.execute(sql_code,(company_name,link,prob))
                conn.commit()
            print(f"Added Link {link} for Company Name {company_name} with probability {prob}")
            
        time.sleep(5)

    except Exception as e:
        print("Error in urladder.")
        print(e)


  