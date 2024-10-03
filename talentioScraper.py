import requests
from bs4 import BeautifulSoup


result = []


def assign_data_based_on_header(header, data, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info):
  # 項目名とデータを受け取り、適した変数に格納
  
  if header == "職種 / 募集ポジション":
      position = data
  elif header in ["勤務地", "勤務場所"]:
      location = location + "\n" + data if location else data
  elif header in ["雇用形態", "試用機関"]:
      employment_type = employment_type + "\n" + data if employment_type else data
  elif header in ["職務内容", "業務内容"]:
      job_description = job_description + "\n" + data if job_description else data
  elif header in ["必要なスキル/資格", "求めるスキル・経験【必須（MUST)】", "求めるスキル・経験【歓迎（WANT）】", "求める人物像"]:
      required_skills = required_skills + "\n" + data if required_skills else data
  elif header in ["給与", "給与備考", "昇給"]:
      salary = salary + "\n" + data if salary else data
  elif header in ["勤務時間", "就業時間", "所定時間外労働", "勤務体系", "休日・休暇"]:
      work_system = work_system + "\n" + data if work_system else data
  elif header in ["待遇・福利厚生", "福利厚生", "保険"]:
      benefits = benefits + "\n" + data if benefits else data
  elif header == "募集背景":
      background = data
  elif header in ["選考プロセス", "採用プロセス", "選考フロー", "選考の流れ"]:
      selection_process = selection_process + "\n" + data if selection_process else data
  elif header == "応募方法":
      application_method = data
  elif header in ["掲載日", "応募締切日"]:
      posting_date_deadline = posting_date_deadline + "\n" + data if posting_date_deadline else data
  elif header in ["特記事項", "定年", "その他"]:
      other_notes = other_notes + "\n" + data if other_notes else data
  elif header in ["会社名", "企業名", "設立", "設立年月日", "代表者", "事業内容", "資本金", "本社所在地", "従業員数", "社員数"]:
      company_info = company_info + "\n" + data if company_info else data
  return position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info

  
def process_job_page(url):
  # 詳細ページのスクレイピング

  # 項目名ごとに変数を初期化
  overview, job_title, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

  # 会社の詳細情報ページを取得
  try:
    res = requests.get(url)
    res.raise_for_status()
  except requests.RequestException as e:
    print(f"詳細ページの取得に失敗しました。 {url}: {e}")
    return None

  soup = BeautifulSoup(res.text, "html.parser")

  # 「概要」を代入
  corporate_overview = soup.find("section", class_="pg-markdown jsc-markdown-text")
  overview = corporate_overview.text if corporate_overview else ""

  # 「求人タイトル」を代入
  corporate_name = soup.find("h1", class_="sg-corporate-name")
  job_title = corporate_name.text if corporate_name else ""

  # <tr><th>「項目名」</th><td>「データ」</td></tr>を要素とする配列itemsを作成
  page_body = soup.find("article", class_="pg-body")
  table_rows = page_body.find_all("tr")
  items = [table_row for table_row in table_rows]

  # 配列itemsの要素を一つずつ取り出し、hrmosの対応項目と一致した場合にその項目に代入
  for item in items:
    table_header = item.find("th").text.strip()
    table_data = item.find("td").text.strip()

    #ヘッダー、データ及び項目名を引数に関数呼び出し
    position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info = assign_data_based_on_header(
        table_header, table_data, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info
    )

  # オブジェクトにデータを整理
    data = {
        "概要": overview,  # 募集背景 仕事のやりがい・魅力 業務内容 主な利用技術・開発環境
        "求人タイトル": job_title,  # シート2に添付の画像を参照
        "募集ポジション": position,  # 職種名
        "勤務地": location,  # 勤務地 勤務場所
        "雇用形態": employment_type,  # 雇用形態 試用期間
        "仕事内容・業務内容": job_description,  # 職務内容 業務内容
        "求めるスキル・資格": required_skills,  # 必須スキル・経験 歓迎スキル・経験 必須スキル 歓迎スキル 求める人物像 求める人物像/スキル
        "給与": salary,  # 給与 給与備考 昇給
        "勤務体系": work_system,  # 勤務時間 就業時間 所定時間外労働 勤務体系 休日・休暇
        "福利厚生": benefits,  # 待遇・福利厚生 福利厚生 保険
        "募集の背景": background,  # 募集背景
        "選考プロセス": selection_process,  # 選考プロセス 選考フロー
        "応募方法": application_method,  # 応募方法
        "掲載日/応募締切日": posting_date_deadline,  # 掲載日 応募締切日
        "その他の特記事項": other_notes,  # その他の特記事項 参考情報一覧
        "会社情報": company_info  # 会社名 企業名 設立 設立年月日 代表者 事業内容 資本金 本社所在地 従業員数
    }


    return data



#会社ページを取得
company_url = "https://hrmos.co/pages/superstudio/jobs"

try:
  res = requests.get(company_url)
  res.raise_for_status()
except requests.RequestException as e:
  print(f"会社ページの取得に失敗しました。 URL: {e}")
  exit()

soup = BeautifulSoup(res.text, "html.parser")


#会社の求人一覧から、求人ごとの詳細へ遷移するURLを配列で取得
joblist = soup.find("section", id="jsi-joblist")
links = joblist.find_all("a")
urls = [link.get("href") for link in links]


#取得したURLを一つずつ取り出し、求人の詳細情報ページを処理
for url in urls:
  job_data = process_job_page(url)
  if job_data:
    result.append(job_data)


print(result)