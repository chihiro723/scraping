import requests
from bs4 import BeautifulSoup


result = []
count = 0
  
def process_job_page(url):
  global result, count
  count += 1
  print(count)
  # 会社の詳細情報ページを取得
  try:
    res = requests.get(url)
    res.raise_for_status()
  except requests.RequestException as e:
    print(f"詳細ページの取得に失敗しました。 {url}: {e}")
    return None

  soup = BeautifulSoup(res.text, "html.parser")

  # <tr><th>「項目名」</th><td>「データ」</td></tr>を要素とする配列itemsを作成
  page_body = soup.find("article", class_="pg-body")
  table_rows = page_body.find_all("tr")
  items = [table_row for table_row in table_rows]

  # 配列itemsの要素を一つずつ取り出し、hrmosの対応項目と一致した場合にその項目に代入
  for item in items:
    table_header = item.find("th").text.strip()
    result.append(table_header)
    result = list(set(result))
    


company_urls = ["superstudio", "timee", "toshiba", "sawai", "kuraray", "monotaro", "uzabase", "jcom", "adk", "avex"]

for company_url in company_urls:
    try:
        res = requests.get(f"https://hrmos.co/pages/{company_url}/jobs")
        res.raise_for_status()
    except requests.RequestException as e:
        exit()

    soup = BeautifulSoup(res.text, "html.parser")


    #会社の求人一覧から、求人ごとの詳細へ遷移するURLを配列で取得
    joblist = soup.find("section", id="jsi-joblist")
    links = joblist.find_all("a")
    urls = [link.get("href") for link in links]


    #取得したURLを一つずつ取り出し、求人の詳細情報ページを処理
    for url in urls:
        job_data = process_job_page(url)



unique = list(set(result))
print(unique)
print(count)