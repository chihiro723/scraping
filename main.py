from fastapi import FastAPI
from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument('--headless')  # ヘッドレスモードを有効にする


def get_recruitment_info_from_hrmos(company):

    result = []

    def assign_data_based_on_header(header, data, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info):
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
        elif header in ["選考プロセス", "採用プロセス", "選考フロー", "選考の流れ"]:
            selection_process = selection_process + "\n" + data if selection_process else data
        elif header == "応募方法":
            application_method = data
        elif header in ["掲載日", "応募締切日"]:
            posting_date_deadline = posting_date_deadline + "\n" + data if posting_date_deadline else data
        elif header in ["会社名", "企業名", "設立", "設立年月日", "代表者", "事業内容", "資本金", "本社所在地", "従業員数", "社員数"]:
            company_info = company_info + "\n" + data if company_info else data
        return position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info

    def process_job_page(url):
        # 詳細ページのスクレイピング
        overview, job_title, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info = "", "", "", "", "", "", "", "", "", "", "", "", "", ""

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
        overview = str(corporate_overview) if corporate_overview else ""

        # 「求人タイトル」を代入
        corporate_name = soup.find("h1", class_="sg-corporate-name")
        job_title = str(corporate_name) if corporate_name else ""

        # <tr><th>「項目名」</th><td>「データ」</td></tr>を要素とする配列itemsを作成
        page_body = soup.find("article", class_="pg-body")
        table_rows = page_body.find_all("tr")
        items = [table_row for table_row in table_rows]

        # 配列itemsの要素を一つずつ取り出し、hrmosの対応項目と一致した場合にその項目に代入
        for item in items:
            table_header = item.find("th").text.strip()
            table_data = str(item.find("td"))

            # ヘッダー、データ及び項目名を引数に関数呼び出し
            position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info = assign_data_based_on_header(
                table_header, table_data, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info
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
            "選考プロセス": selection_process,
            "応募方法": application_method,
            "掲載日/応募締切日": posting_date_deadline,
            "会社情報": company_info
        }

        return data
    

    #会社ページを取得
    try:
        res = requests.get(f"https://hrmos.co/pages/{company}")
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
    
def get_recruitment_info_from_herp(company):
    
    result = []

    def assign_data_based_on_header(header, data, overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info):
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
        elif header == "選考プロセス":
            selection_process = selection_process + "\n" + data if selection_process else data
        elif header == "応募方法":
            application_method = data
        elif header in ["公開日", "募集終了日", "募集期間"]:
            posting_date_deadline = posting_date_deadline + "\n" + data if posting_date_deadline else data
        elif header in ["会社名", "企業名", "設立", "設立年月日", "代表者", "事業内容", "資本金", "本社所在地", "従業員数",]:
            company_info = company_info + "\n" + data if company_info else data
        return overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info

    def process_job_page(url):
        
    # 詳細ページのスクレイピング

    # 項目名ごとに変数を初期化
        overview, job_title, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info = "", "", "", "", "", "", "", "", "", "", "", "", "", ""

        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"詳細ページの取得に失敗しました。 : {e}")

        soup = BeautifulSoup(res.text, "html.parser")


        requisition_header_name = soup.find("h1", class_="requisition-header__name")
        job_title = str(requisition_header_name) if requisition_header_name else ""


        header_data_pairs = []

        card_contents = soup.find_all("div", class_="card__content")
        for card_content in card_contents:
            header, data = card_content.find("h2", class_="with-heading__heading heading"), card_content.find("div", class_="multiline-text js-autolink")
            if header is not None and data is not None:
                header_data_pairs.append({"header": header.text.strip(), "data": str(data)})


        tables = soup.find_all("table", class_="kv-table")
        for table in tables:
            table_rows = table.find_all("tr")
            for table_row in table_rows:
                header = table_row.find("th")
                data = table_row.find("td")
                header_data_pairs.append({"header": header.text.strip(), "data": str(data)})

        
        for header_data_pair in header_data_pairs:
            header, data = header_data_pair["header"], header_data_pair["data"]
            overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info = assign_data_based_on_header(
            header, data, overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info
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
            "選考プロセス": selection_process, #選考プロセス
            "応募方法": application_method, #応募方法
            "掲載日/応募締切日": posting_date_deadline, #公開日 募集終了日 募集期間
            "会社情報": company_info #会社名 企業名 設立 設立年月日 代表者 事業内容 資本金 本社所在地 従業員数
        }

        return data


    #会社ページを取得
    domain = "https://herp.careers/"

    try:
        res = requests.get(f"https://herp.careers/v1/{company}")
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

def get_recruitment_info_from_talentio(company):
    
    result = []

    def assign_data_based_on_header(header, data, overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info):
        # 項目名とデータを受け取り、適した変数に格納

        if header in [
        "企業・事業概要", "HR Tech 事業部について", "わたしたちについて", 
        "私たちのCredo", "EXAWIZARDSとは", "プロジェクト例", 
        "もっと知りたい方へ", "情報", "Who we are", "直近のリリース情報",
        "タレンティオについて", "事業内容"
        ]:
            overview = overview + "\n" + data if overview else data
        elif header in [
            "求めるポジション", "業務内容", "仕事内容", "担当いただくプロダクト", 
            "担当いただくプロダクト紹介", "仕事のやりがい・働く魅力", 
            "ポジションの面白さ", "ポジションの魅力", "ポジションの魅力・得られるスキル", 
            "募集背景", "配属部署"
        ]:
            position = position + "\n" + data if position else data
        elif header in ["勤務地", "勤務場所"]:
            location = location + "\n" + data if location else data
        elif header in ["雇用条件等", "雇用形態", "契約期間", "試用期間"]:
            employment_type = employment_type + "\n" + data if employment_type else data
        elif header in ["仕事内容", "業務内容", "職務内容", "プロダクト詳細"]:
            job_description = job_description + "\n" + data if job_description else data
        elif header in [
            "応募資格（必須）", "必須条件", "応募資格（歓迎）", "歓迎条件", 
            "求める人物像", "求める人材", "求める人物像等", "キャリアパス"
        ]:
            required_skills = required_skills + "\n" + data if required_skills else data
        elif header in ["給与", "賃金", "想定年収", "昇給・賞与"]:
            salary = salary + "\n" + data if salary else data
        elif header in ["勤務時間", "残業", "休日", "休暇", "勤務形態", "勤務形態について", "働き方"]:
            work_system = work_system + "\n" + data if work_system else data
        elif header in ["福利厚生", "社会保険", "受動喫煙防止措置", "諸手当"]:
            benefits = benefits + "\n" + data if benefits else data
        elif header in [
            "選考フロー", "選考プロセス", "面接プロセス", "補足", "関連資料"
        ]:
            selection_process = selection_process + "\n" + data if selection_process else data
        elif header == "応募方法":
            application_method = data
        elif header in ["掲載日", "応募締切日"]:
            posting_date_deadline = posting_date_deadline + "\n" + data if posting_date_deadline else data
        elif header in ["会社情報"]:
            company_info = company_info + "\n" + data if company_info else data

        return overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info

    def process_job_page(url):

        # 詳細ページのスクレイピング

        # 項目名ごとに変数を初期化
        overview, job_title, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info = "", "", "", "", "", "", "", "", "", "", "", "", "", ""

        child_driver = webdriver.Chrome(options=options)
        child_driver.get(url)
        wait = WebDriverWait(child_driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "open-page-job-details")))
        html = child_driver.page_source.encode('utf-8')
        child_driver.quit()
        soup = BeautifulSoup(html, "html.parser")

        job_details = soup.find('div', class_="open-page-job-details")

        # 「求人タイトル」を代入
        job_title = str(job_details.find('h2', class_="open-page-job-details__job-title"))

        # [会社情報」を代入
        # なぜかdlタグの中身を取得することができない。
        other_details = soup.find('div', class_="open-page-other-details")
        company_info = str(other_details.find('dl'))

        dts = job_details.find_all('dt', class_="open-page-job-details__title")
        headers = [x.text for x in dts]
        
        dds = job_details.find_all('dd', class_="open-page-job-details__markdown")
        datas = [str(x) for x in dds]
        if len(headers) == len(datas):
            header_data_pairs = [{"header": h, "data": d} for h, d in zip(headers, datas)]

        #ヘッダー、データ及び項目名を引数に関数呼び出し
        for index, header_data_pair in enumerate(header_data_pairs):
            header, data = header_data_pair["header"], header_data_pair["data"]
            overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info = assign_data_based_on_header(
            header, data, overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info
            )

        # オブジェクトにデータを整理
        data = {
            "概要": overview,  # 企業・事業概要、HR Tech 事業部について、わたしたちについて、私たちのCredo、EXAWIZARDSとは、プロジェクト例、もっと知りたい方へ、情報、Who we are、直近のリリース情報
            "求人タイトル": job_title,  # サイト上部
            "募集ポジション": position,  # 求めるポジション、業務内容、仕事内容、担当いただくプロダクト、担当いただくプロダクト紹介、仕事のやりがい・働く魅力、ポジションの面白さ、ポジションの魅力、ポジションの魅力・得られるスキル、募集背景
            "勤務地": location,  # 勤務地 勤務場所
            "雇用形態": employment_type,  # 雇用条件等、雇用形態、契約期間、試用期間
            "仕事内容・業務内容": job_description,  # 仕事内容、業務内容、職務内容、タレンティオについて、プロダクト詳細
            "求めるスキル・資格": required_skills,  # 応募資格（必須）、必須条件、応募資格（歓迎）、歓迎条件、求める人物像、求める人材、求める人物像等、キャリアパス
            "給与": salary,  # 給与、賃金、想定年収、昇給・賞与
            "勤務体系": work_system,  # 勤務時間、残業、休日、休暇、勤務形態、勤務形態について、働き方
            "福利厚生": benefits,  # 福利厚生、社会保険、受動喫煙防止措置、諸手当
            "選考プロセス": selection_process,  # 選考フロー、選考プロセス、面接プロセス、補足、関連資料
            "応募方法": application_method,  # 
            "掲載日/応募締切日": posting_date_deadline,  #　
            "会社情報": company_info  # セクションごと取得
        }

        return data

    #会社ページを取得
    if "/pages/" in company:
        job_data =  process_job_page(company)
        if job_data:
            result.append(job_data)
    else:
        driver = webdriver.Chrome(options=options)
        driver.get(company)
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
            if job_data:
                result.append(job_data)
    
    return result


# uvicorn main:app --reload   ローカルサーバー立ち上げ

class Item(BaseModel):
    company_url: str

app = FastAPI()

@app.post("/")
async def get_recruitment_info(item: Item):

    target_company_url = item.company_url

    if target_company_url.startswith("https://hrmos.co"):
        company = target_company_url.split("pages/")[1].rstrip("/")
        if not company.endswith("jobs"):
            company += "/jobs"
        api_response = get_recruitment_info_from_hrmos(company)
    elif target_company_url.startswith("https://herp.careers/v1"):
        company = target_company_url.split("v1/")[1].rstrip("/")
        api_response = get_recruitment_info_from_herp(company)
    else:
        company = target_company_url.rstrip("/")
        api_response = get_recruitment_info_from_talentio(company)

    return api_response


