from fastapi import FastAPI
from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup

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

        # ヘッダー、データ及び項目名を引数に関数呼び出し
        position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info = assign_data_based_on_header(
            table_header, table_data, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info
        )

    # オブジェクトにデータを整理
    data = {
        "概要": overview,
        "求人タイトル": job_title,
        "募集ポジション": position,
        "勤務地": location,
        "雇用形態": employment_type,
        "仕事内容・業務内容": job_description,
        "求めるスキル・資格": required_skills,
        "給与": salary,
        "勤務体系": work_system,
        "福利厚生": benefits,
        "募集の背景": background,
        "選考プロセス": selection_process,
        "応募方法": application_method,
        "掲載日/応募締切日": posting_date_deadline,
        "その他の特記事項": other_notes,
        "会社情報": company_info
    }

    return data



class Item(BaseModel):
    company_url: str

app = FastAPI()

@app.post("/")
async def get_recuruitment_info(item: Item):
    
    result = []

    # 会社ページを取得
    # company_url = "https://hrmos.co/pages/superstudio/jobs"
    company_url = item.company_url

    try:
        res = requests.get(company_url)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"会社ページの取得に失敗しました。 URL: {e}")
        exit()

    soup = BeautifulSoup(res.text, "html.parser")

    
		# 会社の求人一覧から、求人ごとの詳細へ遷移するURLを配列で取得
    joblist = soup.find("section", id="jsi-joblist")
    links = joblist.find_all("a")
    urls = [link.get("href") for link in links]

    
		# 取得したURLを一つずつ取り出し、求人の詳細情報ページを処理
    for url in urls:
        job_data = process_job_page(url)
        if job_data:
            result.append(job_data)

    return result
