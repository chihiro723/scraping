import requests
from bs4 import BeautifulSoup

result = []
count = 0

def process_job_page(url):
  # 詳細ページのスクレイピング
  global result, count
  count += 1
  print(count)
  try:
    res = requests.get(url)
    res.raise_for_status()
  except requests.RequestException as e:
    print(f"詳細ページの取得に失敗しました。 : {e}")

  soup = BeautifulSoup(res.text, "html.parser")

  requisition_header_name = soup.find("h1", class_="requisition-header__name")
  job_title = requisition_header_name.text.strip() if requisition_header_name else ""


  try:
    res = requests.get(url)
    res.raise_for_status()
  except requests.RequestException as e:
    print(f"詳細ページの取得に失敗しました。 : {e}")

  soup = BeautifulSoup(res.text, "html.parser")


  requisition_header_name = soup.find("h1", class_="requisition-header__name")
  job_title = requisition_header_name.text.strip() if requisition_header_name else ""


  header_data_pairs = []

  card_contents = soup.find_all("div", class_="card__content")
  for card_content in card_contents:
    header, data = card_content.find("h2", class_="with-heading__heading heading"), card_content.find("div", class_="multiline-text js-autolink")
    if header is not None and data is not None:
      result.append(header.text.strip())

  tables = soup.find_all("table", class_="kv-table")
  for table in tables:
    table_rows = table.find_all("tr")
    for table_row in table_rows:
      header = table_row.find("th")
      data = table_row.find("td")
      result.append(header.text.strip())




company_urls = ["gmomedia", "tebiki", "kaminashi", "turing", "asobica", "nstock", "gakken", "kwork", "primenumber", "digitalsaiyo"]

for company_url in company_urls:

    try:
        res = requests.get(f"http://herp.careers/v1/{company_url}")
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"会社ページの取得に失敗しました。 URL: {e}")

    soup = BeautifulSoup(res.text, "html.parser")


    #会社の求人一覧から、求人ごとの詳細へ遷移するURLを配列で取得
    joblist = soup.find("div", class_="requisition-list")
    links = joblist.find_all("a", class_="with-heading requisition-list-card__header-anchor")
    urls = [link.get("href") for link in links]

    for url in urls:
       process_job_page(f"https://herp.careers/{url}")
       print(result)

unique_list = list(set(result))

print(unique_list)
print(count)