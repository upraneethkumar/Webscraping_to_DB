from datetime import date
from bs4 import BeautifulSoup
import requests
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import yaml



print("Mention the skills which you don't have: ")
unfamiliar_skills = input('>')
print(f"Filtering out {unfamiliar_skills}")

Base = declarative_base()

class Jobs(Base):
    __tablename__ = 'Jobs'
    id = Column(Integer, primary_key=True)
    company_name = Column(String(50))
    skills = Column(String(255))
    location = Column(String(255))
    experience = Column(String(50))
    last_scraped_date = Column(DateTime)
    more_info = Column(String(255))


def getdbconfigfromyaml():
    INITIALIZEYAML_OBJ = None
    with open('instance_settings.yaml', 'r') as stream:
        try:
            INITIALIZEYAML_OBJ = yaml.load(stream, Loader=yaml.FullLoader)
            print(INITIALIZEYAML_OBJ.get('DB_USERNAME'))
        except yaml.YAMLError as exc:
            print("error while reading yaml")
            print(exc)
            raise
    return INITIALIZEYAML_OBJ


def getMariDbSession():
    INITIALIZEYAML_OBJ = getdbconfigfromyaml()
    s = 'mariadb+mariadbconnector://' + INITIALIZEYAML_OBJ.get('DB_USERNAME') + \
    ':' + INITIALIZEYAML_OBJ.get('DB_PASSWORD') + '@' + \
    INITIALIZEYAML_OBJ.get('HOST') + '/' + INITIALIZEYAML_OBJ.get('DB_NAME')

    # print(s)
    # engine = create_engine(s)

    engine = create_engine('mariadb+mariadbconnector://root:12345678@127.0.0.1:3307/jobs')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    dbsession = Session()
    return dbsession
    # job1 = Jobs(id=1, company_name='abc')
    # dbsession.add(job1)
    # dbsession.commit()


import os
import requests
from bs4 import BeautifulSoup
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Assuming the Jobs class and getMariDbSession function are defined elsewhere in your code
# from your_database_module import Jobs, getMariDbSession

def find_jobs():
    html_text = requests.get(
        'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=python&txtLocation=').text
    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

    session = getMariDbSession()

    if not os.path.exists('result'):
        os.makedirs('result')

    for index, job in enumerate(jobs):
        company_name = job.find('h3', class_='joblist-comp-name').text.strip()
        skills = job.find('span', class_='srp-skills').text.replace(' ', '').strip()
        location = job.find('span', title=True).text.strip()
        experience = job.find('ul', class_='top-jd-dtl clearfix').li.text.replace("card_travel", "").strip()
        more_info = job.header.h2.a['href']

        with open(f'result/{index}.txt', 'w') as f:
            f.write(f"Company Name: {company_name}\n")
            f.write(f"Required Skills: {skills}\n")
            f.write(f"Location: {location}\n")
            f.write(f"Required Experience: {experience}\n")
            f.write(f"More Info: {more_info}\n")
        print(f"File Saved: {index}")

        newJob = Jobs(
            id=index,
            company_name=company_name,
            skills=skills,
            location=location,
            experience=experience,
            last_scraped_date=date.today(),
            more_info=more_info
        )
        session.add(newJob)
        session.commit()


find_jobs()
