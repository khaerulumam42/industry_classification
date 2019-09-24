import requests
import re
import yaml
import sqlalchemy
import mysql.connector

from bs4 import BeautifulSoup
from mysql.connector import Error
from datetime import datetime
from dateparser import parse

with open('config_db.yml', 'r') as f:
    config = yaml.load(f)
# connect to db engine using mysql and mysqlconnector
connection = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(config["user"], \
    config["password"], config["host"], config["port"], config["dbname"])
conn = sqlalchemy.create_engine(connection)

# create table if not exists
try:
    create_table_jobstreet = """CREATE TABLE IF NOT EXISTS jobstreet ( 
                             job_id int(11) NOT NULL,
                             url_logo varchar(250),
                             company_name varchar(250),
                             location varchar(250),
                             position varchar(250),
                             industry varchar(250),
                             min_company_size int(11),
                             max_company_size int(11),
                             job_desc varchar(250),
                             posted DATE NOT NULL,
                             PRIMARY KEY (job_id)) """

    conn.execute(create_table_jobstreet) #create db
Exception as e:
    print("error while create db ", e)

def update_data_db(df):
    pass
    
def process_company_size(soup):
    if soup.find('p',{'id':'company_size'}):
        company_size = soup.find('p',{'id':'company_size'}).text 
    else:
        company_size = None
    size = []
    # find some digit on text
    if company_size != None:
        for token in company_size.split():
            if token.isdigit():
                size.append(int(token))
            else:
                pass
    # if no company size available, we use 0 upto 1
    else:
        size = [0,1]
    # add max company size if greater than 5000
    if len(size) == 1:
        size.append(99999)

    return size

def process_job_desc(soup):
    if soup.find('div',{'id':'job_description'}):
        job_desc = soup.find('div',{'id':'job_description'}).text
    else:
        job_desc = None

    return job_desc

def process_date_posted(soup):
    if job_soup.find('p', {'id':'posting_date'}):
        date_str = job_soup.find('p', {'id':'posting_date'}).text.split(': ')[-1]
    else:
        date_str = None
    # format into datetime format
    try:
        date_posted = parse(date_str).strftime('%d/%m/%y')
    except TypeError:
        # if error such as None return as January 1st 1990
        date_posted = parse("1/January/1990").strftime('%d/%m/%y')
    
    return date_posted

def job_page(position, job_id):
    # visit job details webpage
    route = position.lower().replace(" ","-")+"-"+str(job_id)
    url = 'https://www.jobstreet.co.id/id/job/{}'.format(route)
    job_webpage = requests.get(url, headers=headers, params=pay_load)
    job_soup = BeautifulSoup(job_webpage.text, 'html')
    # process to min and max size
    min_size, max_size = process_company_size(job_soup)
    # we will cleaning job desc ion preprocessing
    job_desc = process_job_desc(job_soup)
    # format date posted into datetime formatting
    date_posted = process_date_posted(job_soup)
        
    return min_size, max_size, job_desc, date_posted
    
def process_url_logo(detail_job):
    if detail_job.find('img', {'class':"img-company-logo"}):
        logo =  detail_job.find('img', {'class':"img-company-logo"})["data-original"]
    else:
        logo = None
    return logo

def process_company_name(detail_job):
    if detail_job.find('a', {'class':"company-name"}):
        company_name = detail_job.find('a', {'class':"company-name"}).span.string
    else:
        company_name = None

    return company_name

def process_location(detail_job):
    if detail_job.find('li', {'class':"job-location"}):
        loc = detail_job.find('li', {'class':"job-location"})["title"]
    else:
        loc = None

    return loc

def process_position(detail_job):
    if detail_job.find('a',{'class':'position-title-link'}):
        pos = detail_job.find('a',{'class':'position-title-link'})["data-job-title"] 
    else:
        pos = None

    return pos

def process_industry(detail_job):
    if detail_job.find('a',{'class':'text-muted'}):
        industry = re.search(r'Lowongan (.*?) di', industry_title["title"]).group(1)
    else:
        industry = None
    
    return industry

def process_job_id(detail_job):
    if detail_job.find('a',{'class':'position-title-link',\
        'data-job-id':re.compile(r'.*')}):
        job_id = detail_job.find('a',{'class':'position-title-link',\
            'data-job-id':re.compile(r'.*')})["data-job-id"]      
    else:
        job_id = None
    
    return job_id

def get_all_data(soup):
    # initiate all list data
    urls_logo, companies_name, locations, positions, industries, jobs_id, min_companies_size, max_companies_size, jobs_desc, dates_posted = [[] for i in range(10)]
    
    for detail_job in soup.find_all('div',{'class':'panel-body','id':re.compile(r'job_ad_(\d+)$')}):
        urls_logo.append(process_url_logo(detail_job))
        companies_name.append(process_company_name(detail_job))
        locations.append(process_location(detail_job))
        industries.append(process_industry(detail_job))

        position = process_position(detail_job)
        positions.append(position)
        job_id = process_job_id(detail_job)
        jobs_id.append(job_id)
        
        min_size, max_size, job_desc, date_posted = job_page(position, job_id)
        min_companies_size.append(min_size)
        max_companies_size.append(max_size)
        jobs_desc.append(job_desc)
        dates_posted.append(date_posted)
        
    return urls_logo, companies_name, locations, positions, industries, jobs_id, min_companies_size, max_companies_size, jobs_desc, dates_posted

def main():
    URL = "https://www.jobstreet.co.id/id/job-search/job-vacancy.php?ojs=6"
    avail = True
    s = requests.session()
    page = 1
    urls_logo_all, companies_name_all, locations_all, positions_all, industries_all, jobs_id_all, min_companies_size_all, max_companies_size_all, jobs_desc_all, date_posted_all = [[] for i in range(10)]
    while avail:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; \
            Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/66.0.3359.139 Safari/537.36'}

        pay_load = {'key':'','area':1,'option':1,'pg':None,'classified':1,\
            'src':16,'srcr':12}
        pay_load['pg'] = page
        webpage = requests.get(URL, headers=headers, params=pay_load)
        soup = BeautifulSoup(webpage.text,'html.parser')
        links = soup.find_all('a',{'class':'position-title-link',\
            'data-job-id':re.compile(r'.*')})
        # stop when np links available, end of page
        if not len(links):
            avail = False
        else:
            urls_logo, companies_name, locations, positions, industries, jobs_id, min_companies_size, max_companies_size, jobs_desc, date_posted = get_all_data(soup)
            urls_logo_all.extend(urls_logo)
            companies_name_all.extend(companies_name)
            locations_all.extend(locations)
            positions_all.extend(positions)
            industries_all.extend(industries)
            jobs_id_all.extend(jobs_id)
            min_companies_size_all.extend(min_companies_size)
            max_companies_size_all.extend(max_companies_size)
            jobs_desc_all.extend(jobs_desc)
            date_posted_all.extend(date_posted)

            page += 1
            
    df = pd.DataFrame.from_dict({"job_id":jobs_id_all,
                                "url_logo":urls_logo_all,
                                "company_name":companies_name_all,
                                "location":locations_all,
                                "position":positions_all,
                                "industry":industries_all,
                                "min_company_size":min_companies_size_all,
                                "max_company_size":max_companies_size_all,
                                "job_desc":jobs_desc_all,
                                "posted":date_posted_all})
        
    return df