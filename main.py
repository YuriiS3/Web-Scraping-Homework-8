import json

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import sqlite3


def write_sql(data: list) -> None:
    filename = 'Jobs.db'

    # 1. create table
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    sql = """
        create table if not exists [Jobs] (
            id integer primary key,
            [title] text,
            [url] text
        )
    """
    cursor.execute(sql)

    sql = """
        delete from [Jobs]
    """
    cursor.execute(sql)

    # 2. insert data
    for item in data:
        cursor.execute("""
            insert into [Jobs] ([title], [url])
            values (?, ?)
        """, (item['title'], item['url']))

    conn.commit()
    conn.close()

def parse():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    # driver = webdriver.Chrome()
    max_page = 3

    wait = WebDriverWait(driver, 20)

    result = []

    for page in range(1, max_page):
        driver.get(f'https://jobs.marksandspencer.com/job-search?page={page}')
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ais-Hits-item')))

        jobs = driver.find_elements(By.CLASS_NAME, 'ais-Hits-item')
        for job in jobs:
            title = job.find_element(By.TAG_NAME, 'h3').text
            url = job.find_element(By.TAG_NAME, 'a').get_dom_attribute('href')
            url = 'https://jobs.marksandspencer.com' + url
            result.append({
                'title': title,
                'url': url
            })

    driver.quit()

    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)

    write_sql(result)

if __name__ == '__main__':
    parse()
