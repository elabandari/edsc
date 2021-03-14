# Author : Kevin Shahnazari
# Date: March 13th 2021

"""
This Script Acts as a bridge between the SQL server
and the job scraper. Meaning it gets what it has to 
scrape next from the SQL server, passes it to the scraper
and then returns the results for the SQL server.

"""

from Scrapejobbank import jobbankScraper
import psycopg2
import json
import datetime
import time

def add_one_job():
    # Get SQL credentials and connect
    with open('connection.json') as f:
        db = json.load(f)

    conn = psycopg2.connect(database=db['dbname'], user=db['user'], password=db['password'], host=db['host'])

    try:
        # Get A company name that we haven't scrapped yet so that we could scrape it!
        with conn, conn.cursor() as cur:
            cur.execute("""SELECT id_mapping.businessname
            FROM public.id_mapping
            LEFT JOIN public.jobbank_employer_posting ON jobbank_employer_posting.business_name = id_mapping.businessname
            WHERE jobbank_employer_posting.business_name IS NULL ORDER BY RANDOM() LIMIT 1""")
            for company_name in cur.fetchall():
                company_name_scrape = company_name[0]

        # Scrape the number of job postings using the function below
        scraper = jobbankScraper()
        num = scraper.scrape_checkjobposting(company_name_scrape)
        # If num is -1 that means somewhere the function has failed therefore we shouldn't Insert anything
        if num != -1:
            # Insert the information
            sql_code = """ INSERT INTO public.jobbank_employer_posting(business_name,num_postings)
            VALUES(%s,%s)"""
            with conn, conn.cursor() as cur:
                cur.execute(sql_code,(company_name,num))
                conn.commit()
                # Print a Success Message
                print(f"Added Company Name {company_name_scrape} with Job posting numbers of {num}")
        

    except Exception as e:
        # Print error message if the code above fails
        print("Error in jobpostadder.")
        print(e)

