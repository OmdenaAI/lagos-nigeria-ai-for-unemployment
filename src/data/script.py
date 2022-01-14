"""Tribute to AI Saturday Lagos"""

import requests
from bs4 import BeautifulSoup
import datetime
import csv
import argparse
import logging

logging.root.setLevel(logging.INFO)

url =  "https://www.linkedin.com/jobs/search/?geoId=105365761&location=Nigeria&sortBy=R&start="

#Creating parser
def get_parser():
    """
    parse command line arguments

    Returns
    -------
    parser - ArgumentParser object

    """
    parser = argparse.ArgumentParser(description="Linkedin Job Scraper")
    parser.add_argument(
        "--output_file_name",
        type=str,
        default="LinkedIn_Jobs.csv",
        help="Name of output file",
        )
    return parser


#creating a function that collects all the jobs url on linkedin
def linkedin (url):
    """
    A function that collects all the jobs url on linkedin
    
    Parameters
    ----------
    url: the linkedin jobs homepage

    Returns
    -------
    job_links (list): a list of links to direct jobs on LinkedIn

    """
    job_links = []
    page_range = [url + str(x) for x in list(range(0, 975, 25))]
    for val in page_range:
        response = requests.get(val)
        soup_object = BeautifulSoup(response.text, "html.parser")

        #getting the links in each page
        page_links = soup_object.findAll("a")
        #print(page_links)
        for links in page_links:
                
                href = links.get("href")
                if (
                    href.startswith("https://ng.linkedin.com/jobs/view/")):
                    job_links.append(href)
    return(job_links)


## function to get the contects

def job_content (job_url: list):
    """
    Parameters
    ----------
    job_url (list): a list of links to direct jobs on LinkedIn 

    Returns
    ------
    title, linkedin_link, jd, company, location, date_posted 
    """
    ##testing a link   
    countss = 0
    title = []
    linkedin_link = []
    jd = []
    company = []
    location = []
    date_posted  = []
    logging.info("Printing  Status code .............")
    for val in job_url:
        link = val 
        
        s = requests.Session()
        job =  s.get(link)
        print(job.status_code)
        countss +=1
        #print(countss)
        if job.status_code == 200: #could also check == requests.codes.ok
            job_soup = BeautifulSoup(job.text, "html.parser")


            #print(job_soup)

            #the job title
            job_title = job_soup.find(
                "h1", attrs={"class": "top-card-layout__title topcard__title"}
            )

            #print((job_title))
            title.append(job_title.text)


            #getting the job description
            job_description = job_soup.find(
                "div", attrs={"class": "show-more-less-html__markup show-more-less-html__markup--clamp-after-5"}
                )
            jd.append(job_description.text.lstrip().rstrip())


            #company name
            company_name = job_soup.find(
                "span", attrs={"class": "topcard__flavor"}
            ) 

            company.append(company_name.text.strip())

            #Location
            job_location = job_soup.find(
                "span", attrs={"class": "topcard__flavor topcard__flavor--bullet"}
            ) #topcard__flavor topcard__flavor--bullet

            location.append(job_location.text.strip())


            #Date Posted 
            #for jobs posted less than a day
            try:
                job_date = job_soup.find(
                "span", attrs={"class": "posted-time-ago__text posted-time-ago__text--new topcard__flavor--metadata"}
                )
                ddate = job_date.text.strip()
                
            #for jobs older than a day
            except AttributeError:
                job_date = job_soup.find(
                "span", attrs={"class": "posted-time-ago__text topcard__flavor--metadata"}
                )
                ddate = job_date.text.strip()
                

            if ( ddate.split(" ")[1] == "day" or\
                    ddate.split(" ")[1] == "days"):
                date_posted.append((datetime.date.today() - datetime.timedelta(days=int(ddate.split(" ")[0]))).isoformat())
            elif (ddate.split(" ")[1] == "week" or\
                    ddate.split(" ")[1] == "weeks"):
                date_posted.append((datetime.date.today() - datetime.timedelta(days=int(ddate.split(" ")[0]) * 7)).isoformat())
            elif (ddate.split(" ")[1] == "month" or\
                    ddate.split(" ")[1] == "months"):
                date_posted.append((datetime.date.today() - datetime.timedelta(days=int(ddate.split(" ")[0]) * 30)).isoformat())
            else:
                date_posted.append((datetime.date.today()).isoformat())

            #link to post
            linkedin_link.append(link)
            #title, linkedin_link, jd, company, location, date_posted 
        else: 
            continue
    print ("Scraping completed")
    return title, linkedin_link, jd, company, location, date_posted 

#writing the jobs to file
def output(output_file_name: str, job_url: list):
    """
    Paramters
    ---------
    output_file_name: the name to be given the the file
    job_url: list of links to individual jobs

    """
    logging.info("Writing jobs to file...")

    title, linkedin_link, jd, company, location, date_posted = job_content (job_url)
    
    with open(output_file_name, "w", newline='', encoding='utf-8') as csv_file:
        field_name = ["Title", "Job Description", "Location", "Compnay Name", "Date Posted", "LinkedIn Link"]
        writer = csv.writer(csv_file)
        writer.writerow(field_name)
        for a,b,c,d,e,f in zip(title, jd, location, company, date_posted, linkedin_link):
            writer.writerow([a,b,c,d,e,f])
        job_num = len(title)
        logging.info(f"Successfully wrote story number {job_num}")
    logging.info(
        f"Scraping done. A total of {job_num} Jobs were scraped!")

 

if __name__ == "__main__":
    
    logging.info("--------------------------------------")
    logging.info("Starting scraping...")
    logging.info("--------------------------------------")
    
    # initialize parser
    parser = get_parser()
    params, unknown = parser.parse_known_args()
    scraped_links = linkedin(url)
    output(params.output_file_name, scraped_links)

""" Author: Abraham Owodunni
    Email: owodunniabraham@gmail.com
    Twitter: @AbrahamOwos
"""