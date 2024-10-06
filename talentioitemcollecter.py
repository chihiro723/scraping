from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

result = []
count = 0

def process_job_page(url):
  global result, count
  # 詳細ページのスクレイピング
  count += 1
  print(count)
  # 会社の詳細情報ページを取得
  options = Options()
  options.add_argument('--headless')  # ヘッドレスモードを有効にする
  driver = webdriver.Chrome(options=options)
  driver.get(url)
  wait = WebDriverWait(driver, 10)
  wait.until(EC.presence_of_element_located((By.CLASS_NAME, "open-page-job-details")))
  html = driver.page_source.encode('utf-8')
  driver.quit()
  soup = BeautifulSoup(html, "html.parser")


  job_details = soup.find('div', class_="open-page-job-details")

  # 「求人タイトル」」を代入
  job_title = job_details.find('h2', class_="open-page-job-details__job-title").string.strip()

  # なぜかdlタグの中身が取得できない
  other_details = soup.find('div', class_="open-page-other-details")
  company_info = other_details.find('dl')

  dts = job_details.find_all('dt', class_="open-page-job-details__title")
  headers = [x.text for x in dts]
  
  for header in headers:
    result.append(header)
    result = list(set(result))
  
#会社ページを取得
company_urls = ["https://open.talentio.com/r/1/c/smsc/homes/3770", "https://open.talentio.com/r/1/c/exwzd/homes/4039", "https://recruit.talentio.co.jp/r/1/c/talentio/homes/1", "https://open.talentio.com/r/1/c/feedforce/pages/79563", "https://open.talentio.com/r/1/c/sansan/pages/99281?_gl=1*1tqu85u*_ga*MTY1MDcyOTE0NC4xNzI4MTAyNTQy*_ga_EN18Q6V0JW*MTcyODIwNzY1NC4yLjAuMTcyODIwNzY1NC4wLjAuMA..", "https://open.talentio.com/r/1/c/sansan/pages/98203?_gl=1*1h5j4ay*_ga*MTY1MDcyOTE0NC4xNzI4MTAyNTQy*_ga_EN18Q6V0JW*MTcyODIwNzY1NC4yLjAuMTcyODIwNzcwOC4wLjAuMA..", "https://open.talentio.com/r/1/c/studist-recruit/pages/92304", "https://open.talentio.com/r/1/c/studist-recruit/pages/75537"]

for company_url in company_urls:

    if "pages" in company_url:
        job_data = process_job_page(company_url)
    else:
        options = Options()
        options.add_argument('--headless')  # ヘッドレスモードを有効にする
        driver = webdriver.Chrome(options=options)
        driver.get(company_url)
        WebDriverWait(driver, 10)

        html = driver.page_source.encode('utf-8')
        driver.quit()
        soup = BeautifulSoup(html, "html.parser")
        link_parent_spans = soup.find_all('span', class_="open-page-home-requisition-list__link open-page-home__link")

        links = []
        for link_parent_span in link_parent_spans:
            link_span = link_parent_span.find('span')
            links.append(link_span)
        urls = [x['data-link-url'] for x in links]

        #取得したURLを一つずつ取り出し、求人の詳細情報ページを処理
        for url in urls:
            job_data = process_job_page(url)



unique = list(set(result))
print(unique)
print(count)
