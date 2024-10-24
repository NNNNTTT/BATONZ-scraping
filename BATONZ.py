import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def batonz_scraping(headers):
    all_urls,company_names = get_item_list1(headers)
    print("ループ終了")
    get_item_list2(all_urls,company_names,headers)   
    
def get_item_list1(headers):
    url = "https://batonz.jp/buyer_needs?sort=is_active_public_offering%3Dtrue&is_active_public_offering=true"
    
    d_list = []
    all_urls = []
    company_names = []

    while True:
        r = requests.get(url,headers=headers)
        sleep(0.1)

        soup = BeautifulSoup(r.text,features='lxml')
        script = soup.select("body > script:nth-child(3)")[0].text
        #正規表現のパターンを指定
        pattern = r'id:(\d+)'
        # パターンに一致する部分を探す
        id_numbers = re.findall(pattern, script)    

        url_list = []

        for id_number in id_numbers:
            urls = "https://batonz.jp/buyer_needs/"+id_number
            url_list.append(urls)
            all_urls.append(urls)

        content = soup.select('#app > div.v-application--wrap > main > div > div > div > div.v-card.v-sheet.theme--light > div > div:nth-child(3) > div.v-data-table.d-none.d-md-block.text-center.buyer-need-simple-table.theme--light > div > table > tbody')
        trs = content[0].find_all('tr')
        for tr,company_url in zip(trs,url_list):
            td = tr.find_all('td', class_='text-start')
            company_name = td[1].get_text()
            company_name = replace_split(company_name)
            company_type = td[2].get_text()
            company_type = remove_first_and_last_newlines(company_type)
            company_industry = td[3].get_text()
            company_industry = replace_split(company_industry)
            company_revenue = td[4].get_text()
            contact_person = td[5].get_text()
            td6 = td[6]
            td6_list = td6.find_all("div",class_="chip-label d-flex align-center justify-center")
            acquisition_needs_list = []
            for item in td6_list:
                item = item.get_text()
                try:
                    item = item.replace("\n", "")
                except:
                    item
                item = item.replace(" ","")
                acquisition_needs_list.append(item)
            acquisition_needs = tuple(acquisition_needs_list)
            acquisition_needs ='//'.join(map(str, acquisition_needs))
            
            
            d = {
                "詳細URL":company_url,
                "会社名":company_name,
                "種別":company_type,
                "業種":company_industry,
                "売上高":company_revenue,
                "担当者":contact_person,
                "買収希望ニーズ":acquisition_needs,
                }
            d_list.append(d)
            company_names.append(company_name)
            print(company_name)
            print(len(company_names))


        next_page_link = soup.select('#buyer-need > li:nth-child(9) > a')  # 例えば、次のページへのリンクがclassが'next-page'の<a>タグ内にあるとする
        if next_page_link:
            url = next_page_link[0].get('href')  # 次のページのURLを取得
        else:
            break  # 次のページがない場合、ループを終了       
        
    df = pd.DataFrame(d_list)
    google_sheets_set(df)

    return all_urls,company_names

def get_item_list2(all_urls,company_names,headers):
    d_list = []
    for all_url,company_name in zip(all_urls,company_names):
        r = requests.get(all_url,headers=headers)
        sleep(0.1)
        soup = BeautifulSoup(r.text,features='lxml')
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(1) > div > div.pt-0.col-md-6.col-12 > div.container.pa-5')
        overview = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(2) > div > div:nth-child(1) > div > div.py-2.vertical-align-middle.col-md-9.col-12')
        acquisition_objective = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(2) > div > div:nth-child(2) > div > div.py-2.vertical-align-middle.col-md-9.col-12')
        acquisition_industry = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(2) > div > div:nth-child(3) > div > div.py-2.vertical-align-middle.col-md-9.col-12')
        acquisition_region = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(2) > div > div:nth-child(4) > div > div.py-2.vertical-align-middle.col-md-10.col-12')
        acquisition_revenue = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(2) > div > div:nth-child(5) > div > div.py-2.vertical-align-middle.col-md-10.col-12')
        acquisition_budget= tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(3) > div > div:nth-child(1) > div > p')
        activities = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(4) > div > div:nth-child(1) > div > div.py-2.vertical-align-middle.col-md-9.col-12')
        industry = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(4) > div > div:nth-child(2) > div > div.py-2.vertical-align-middle.col-md-10.col-12')
        contact_person = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(4) > div > div:nth-child(3) > div > div.py-2.vertical-align-middle.col-md-10.col-12')
        hp_url = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(4) > div > div:nth-child(4) > div > div.py-2.vertical-align-middle.col-md-10.col-12')
        employee_count = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(4) > div > div:nth-child(5) > div > div.py-2.vertical-align-middle.col-md-10.col-12')
        address = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(4) > div > div:nth-child(6) > div > div.py-2.vertical-align-middle.col-md-10.col-12')
        acquisitions_count = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(4) > div > div:nth-child(7) > div > div.py-2.vertical-align-middle.col-md-9.col-12')
        operating_base = tag[0].get_text()
        tag = soup.select('#app > div > main > div > div > div > div.full-screen > div:nth-child(4) > div > div:nth-child(8) > div > div.py-2.vertical-align-middle.col-md-10.col-12')
        revenue = tag[0].get_text()

        acquisition_objective = remove_first_and_last_newlines2(acquisition_objective)
        acquisition_industry = remove_first_and_last_newlines2(acquisition_industry)
        acquisition_region = remove_first_and_last_newlines2(acquisition_region)
        industry = remove_first_and_last_newlines(industry)
        operating_base = remove_first_and_last_newlines2(operating_base)

        d = {
            "url":all_url,
            "会社名":company_name,
            "概要":overview,
            "M&Aの目的":acquisition_objective,
            "買収希望の業種":acquisition_industry,
            "買収希望の地域":acquisition_region,
            "買収希望の売上":acquisition_revenue,
            "買収予算":acquisition_budget,
            "ビジネスモデル・事業内容":activities,
            "業種":industry,
            "担当者":contact_person,
            "ホームページURL":hp_url,
            "従業員数":employee_count,
            "事業所在地":address,
            "M&Aの実績数":acquisitions_count,
            "活動拠点":operating_base,
            "会社・事業の売上高":revenue
        }

        d_list.append(d)
    df = pd.DataFrame(d_list)
    google_sheets_append(df)

def google_sheets_set(df):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'my-project-test-420412-0af5cbd80b89.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE,SCOPES)

    gs = gspread.authorize(credentials)

    SPREADSHEETS_KEY = '1iMpRqF4VmZqEG9xs2EbxC2HeAZ90NdlUfF6txk9sknc'
    worksheet = gs.open_by_key(SPREADSHEETS_KEY).worksheet("バトンズ")

    from gspread_dataframe import set_with_dataframe

    set_with_dataframe(worksheet,df,include_index=False)

def google_sheets_append(df):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials  
    # Google スプレッドシートにアクセスするための認証情報
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = ''
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
    gs = gspread.authorize(credentials)

    # 既存のスプレッドシートとワークシートを開く
    SPREADSHEETS_KEY = "12TLKZfciG1XceAxJTIu788udchRptE-K07WN38dDnxM"
    worksheet = gs.open_by_key(SPREADSHEETS_KEY).worksheet("バトンズ")

    from gspread_dataframe import set_with_dataframe

    set_with_dataframe(worksheet,df,col=8,include_index=False)

def replace_split(text):
    replace_text = text.replace(" ", "")
    line = replace_text.split('\n')
    return line[1]

def remove_first_and_last_newlines(text):
    # 空白を削除（ここで空白を削除する必要はありませんが、元のコードに合わせて残しておきます）
    replace_text = text.replace(" ", "")

    # 最初の改行を見つける
    first_newline_pos = replace_text.find('\n')

    if first_newline_pos != -1:
        # 最初の改行を削除して文字列を連結
        replace_text = replace_text[:first_newline_pos] + replace_text[first_newline_pos+1:]

    # 最後の改行を削除
    if replace_text.endswith('\n'):
        replace_text = replace_text[:-1]

    # 残りの改行を "//" に置き換える
    text_no_newlines = replace_text.replace("\n", "//").replace("\r", "")
    
    return text_no_newlines

def remove_first_and_last_newlines2(text):
    # 空白を削除（ここで空白を削除する必要はありませんが、元のコードに合わせて残しておきます）
    replace_text = text.replace(" ", "")

    # 最初の改行を見つける
    first_newline_pos = replace_text.find('\n')

    if first_newline_pos != -1:
        # 最初の改行を削除して文字列を連結
        replace_text = replace_text[:first_newline_pos] + replace_text[first_newline_pos+1:]

    # 最後の改行を削除
    if replace_text.endswith('\n'):
        replace_text = replace_text[:-1]

    # 残りの改行を "//" に置き換える
    text_no_newlines = replace_text.replace("\n", "/").replace("\r", "")
    
    return text_no_newlines

batonz_scraping(headers)
