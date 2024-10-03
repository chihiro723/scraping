from fastapi import FastAPI
from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup


def get_recruitment_info_from_hrmos():

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
    
    try:
        res = requests.get("https://hrmos.co/pages/superstudio/jobs")
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


def get_recruitment_info_from_herp():
    
    result = []

    def assign_data_based_on_header(header, data, overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info):
    # 項目名とデータを受け取り、適した変数に格納
        if header == "仕事概要":
            overview = data
        if header == "募集職種":
            position = data
        elif header in ["勤務地", "勤務場所"]:
            location = location + "\n" + data if location else data
        elif header in ["雇用形態", "試用機関"]:
            employment_type = employment_type + "\n" + data if employment_type else data
        elif header in ["職務内容", "業務内容"]:
            job_description = job_description + "\n" + data if job_description else data
        elif header in ["必須スキル・経験", "歓迎スキル・経験", "必須スキル", "歓迎スキル", "求める人物像", "求める経験・スキル"]:
            required_skills = required_skills + "\n" + data if required_skills else data
        elif header in ["給与", "給与備考", "昇給"]:
            salary = salary + "\n" + data if salary else data
        elif header in ["勤務時間", "就業時間", "所定時間外労働", "勤務体系", "休日・休暇"]:
            work_system = work_system + "\n" + data if work_system else data
        elif header in ["待遇・福利厚生", "福利厚生", "保険"]:
            benefits = benefits + "\n" + data if benefits else data
        elif header == "募集背景":
            background = data
        elif header == "選考プロセス":
            selection_process = selection_process + "\n" + data if selection_process else data
        elif header == "応募方法":
            application_method = data
        elif header in ["公開日", "募集終了日", "募集期間"]:
            posting_date_deadline = posting_date_deadline + "\n" + data if posting_date_deadline else data
        elif header == "その他の特記事項":
            other_notes = other_notes + "\n" + data if other_notes else data
        elif header in ["会社名", "企業名", "設立", "設立年月日", "代表者", "事業内容", "資本金", "本社所在地", "従業員数",]:
            company_info = company_info + "\n" + data if company_info else data
        return overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info

    def process_job_page(url):
        
    # 詳細ページのスクレイピング

    # 項目名ごとに変数を初期化
        overview, job_title, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

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
                header_data_pairs.append({"header": header.text.strip(), "data": data.text.strip()})


        tables = soup.find_all("table", class_="kv-table")
        for table in tables:
            table_rows = table.find_all("tr")
            for table_row in table_rows:
                header = table_row.find("th")
                data = table_row.find("td")
                header_data_pairs.append({"header": header.text.strip(), "data": data.text.strip()})

        
        for header_data_pair in header_data_pairs:
            header, data = header_data_pair["header"], header_data_pair["data"]
            overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info = assign_data_based_on_header(
            header, data, overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, background, selection_process, application_method, posting_date_deadline, other_notes, company_info
            )

        data = {
            "概要": overview, #仕事概要　　　@
            "求人タイトル": job_title, #「シート3」に添付の画像を参照。  @
            "募集ポジション": position, #募集職種
            "勤務地": location, #勤務地 勤務場所
            "雇用形態": employment_type, #雇用形態 試用期間
            "仕事内容・業務内容": job_description, #職務内容 業務内容
            "求めるスキル・資格": required_skills, #必須スキル・経験 歓迎スキル・経験 必須スキル 歓迎スキル 求める人物像 求める経験・スキル @
            "給与": salary, #給与 給与備考 昇給
            "勤務体系": work_system, #勤務時間 就業時間 所定時間外労働 勤務体系 休日・休暇
            "福利厚生": benefits, #待遇・福利厚生 福利厚生 保険
            "募集の背景": background, #募集背景
            "選考プロセス": selection_process, #選考プロセス
            "応募方法": application_method, #応募方法
            "掲載日/応募締切日": posting_date_deadline, #公開日 募集終了日 募集期間
            "その他の特記事項": other_notes, #その他の特記事項
            "会社情報": company_info #会社名 企業名 設立 設立年月日 代表者 事業内容 資本金 本社所在地 従業員数
        }

        return data



    #会社ページを取得
    company_url = "https://herp.careers/v1/gmomedia"
    domain = "https://herp.careers/"

    try:
        res = requests.get(company_url)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"会社ページの取得に失敗しました。 URL: {e}")

    soup = BeautifulSoup(res.text, "html.parser")


    #会社の求人一覧から、求人ごとの詳細へ遷移するURLを配列で取得
    joblist = soup.find("div", class_="requisition-list")
    links = joblist.find_all("a", class_="with-heading requisition-list-card__header-anchor")
    urls = [domain + link.get("href") for link in links]

    #取得したURLを一つずつ取り出し、求人の詳細情報ページを処理
    for url in urls:
        job_data = process_job_page(url)
        if job_data:
            result.append(job_data)

    return result



# uvicorn main:app --reload   ローカルサーバー立ち上げ

class Item(BaseModel):
    company_url: str

app = FastAPI()

@app.post("/")
async def get_recuruitment_info(item: Item):

    if item.company_url.rstrip("/") == "https://hrmos.co/pages/superstudio/jobs":
        response = get_recruitment_info_from_hrmos()
    elif item.company_url.rstrip("/") == "https://herp.careers/v1/gmomedia":
        response = get_recruitment_info_from_herp()
    return response

