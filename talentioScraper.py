from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

result = []


def assign_data_based_on_header(header, data, overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info):
  # 項目名とデータを受け取り、適した変数に格納
  
  if header in [
    "企業・事業概要", "HR Tech 事業部について", "わたしたちについて", 
    "私たちのCredo", "EXAWIZARDSとは", "プロジェクト例", 
    "もっと知りたい方へ", "情報", "Who we are", "直近のリリース情報"
  ]:
      overview = overview + "\n" + data if overview else data
  elif header in [
      "求めるポジション", "業務内容", "仕事内容", "担当いただくプロダクト", 
      "担当いただくプロダクト紹介", "仕事のやりがい・働く魅力", 
      "ポジションの面白さ", "ポジションの魅力", "ポジションの魅力・得られるスキル", 
      "募集背景"
  ]:
      position = position + "\n" + data if position else data
  elif header in ["勤務地", "勤務場所"]:
      location = location + "\n" + data if location else data
  elif header in ["雇用条件等", "雇用形態", "契約期間", "試用期間"]:
      employment_type = employment_type + "\n" + data if employment_type else data
  elif header in ["仕事内容", "業務内容", "職務内容", "タレンティオについて", "プロダクト詳細"]:
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
  elif header in ["その他の注意事項", "備考"]:
      other_notes = other_notes + "\n" + data if other_notes else data
  elif header in ["会社情報"]:
      company_info = company_info + "\n" + data if company_info else data

  return overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info


def process_job_page(url):
  # 詳細ページのスクレイピング

  # 項目名ごとに変数を初期化
  overview, job_title, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info = "", "", "", "", "", "", "", "", "", "", "", "", "", ""

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

  # 「会社情報」を代入
  other_details = soup.find('div', class_="open-page-other-details")
  company_info = other_details.find('dl')
  

  dts = job_details.find_all('dt', class_="open-page-job-details__title")
  headers = [x.text for x in dts]
  
  dds = job_details.find_all('dd', class_="open-page-job-details__markdown")
  datas = [str(x) for x in dds]
  if len(headers) == len(datas):
    header_data_pairs = [{"header": h, "data": d} for h, d in zip(headers, datas)]

  #ヘッダー、データ及び項目名を引数に関数呼び出し
  for header_data_pair in header_data_pairs:
    header, data = header_data_pair["header"], header_data_pair["data"]
    overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info = assign_data_based_on_header(
      header, data, overview, position, location, employment_type, job_description, required_skills, salary, work_system, benefits, selection_process, application_method, posting_date_deadline, company_info
    )

  # オブジェクトにデータを整理
  #background, other_notesは削除済み
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
company_url = "https://recruit.talentio.co.jp/r/1/c/talentio/pages/79740"

if "pages" in company_url:
  job_data = process_job_page(company_url)
  if job_data:
    result.append(job_data)
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
    if job_data:
      result.append(job_data)

  print(result)
