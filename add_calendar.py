from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(level=logging.DEBUG)
source = 'https://kabuyoho.ifis.co.jp/index.php?action=tp1&sa=report_top&bcode='
# CODE = "1515"

# スクリプトのディレクトリを取得 パスを指定hしないとファイルが生成されなかった
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, './output.txt')


# 決算日取得関数
def get_settle_info(CODE):
    # クローリング
    try:
        logging.debug('read web data cord = ' + CODE)  # logging
        r = requests.get(source + CODE)
        print(r)    
    except ValueError:
        logging.debug('read web data ---> Exception Error')  # vlogging
        return None, 'Exception error: access failed'  
    # スクレイピング
    # これは、HTML全体を示している
    soup = BeautifulSoup(r.content, "html.parser")
    settleInfo = soup.find("div", class_="header_main").text
    settleInfo = re.sub(r'[\n\t]+', ',', settleInfo)  # メタ文字の除去
    settleInfo = re.sub(r'(^,)|(,$)', '', settleInfo)  # 行頭行末のカンマ除去
    settleInfo = re.sub(r'[\xc2\xa0]', '', settleInfo)  # &nbsp(\xc2\xa0)問題の処置
    logging.debug('settleInfo result = ' + settleInfo)  # logging
    # 、、で区切られた、文字列が返ってくる
    print(settleInfo)
    if not settleInfo:
        settleInfo = 'not found'

    return settleInfo


# できすと形式の変更
def transform_style(inputText):
    parts = inputText.split(',')
    # エラー処理
    try:
        date = parts[7].strip()
    except IndexError:
        return "エラー: インデックスが範囲外です。"
    dateParts = date.split('/')
    if len(dateParts) != 3:
        return "日付の形式が正しくありません。"
    formattedDate = f"{dateParts[0]}.{dateParts[1]}.{dateParts[2]}"
    title = parts[1].strip()
    dead = parts[3].strip()
    quarter = parts[5].strip()
    result = f"{formattedDate} {title} {quarter}決算発表 {dead}"
    print(result)
    save_file(result, output_path)
    return result     # 2023.11 07 日鉄鉱業 2Q決算発表


# ファイルへの保存
def save_file(result, output_path):
    with open(output_path, 'w') as f:
        f.write(result)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


# ここのテキストファイルを編集すればおk
def read_schedule():
    f = open('./output.txt')
    data = f.read()
    lines = data.split('\n')
    result_list = lines[0].split()
    f.close()
    return result_list


def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    yearmon = read_schedule()    # '2023.11.07', '日鉄鉱業', '2Q決算発表', '決算発表済']
    a = yearmon[0].split(".")
    print(a)     #
    year = int(a[0])
    mon = int(a[1])
    print(year)
    print(mon)

    if mon == 1 or mon == 3 or mon == 5 or mon == 7 or mon == 8 or mon == 10 or mon == 12:
        num_days = 31
    elif mon == 2:
        num_days = 28
    else:
        num_days = 30
    d_s = int(a[2])
    d_e = int(a[2])
    print(d_s)
    m_s = mon
    m_e = mon
    y_s = year
    y_e = year

    if (mon == 12 and d_e == 31):
        y_e = year + 1
    if (num_days == d_e):
        d_e = 1
        if mon == 12:
            m_e = 1
        else:
            m_e = m_e + 1
    # ---------------------------------------------------------
    event = {
        'summary': '{}'.format(yearmon[1]),
        'location': 'Japan',
        'description': '{}'.format(yearmon[2]),
        'start': {
            'date': '{}-{}-{}'.format(y_s, m_s, d_s),
            'timeZone': 'Japan',
        },
        'end': {
            'date': '{}-{}-{}'.format(y_e, m_e, d_e),
            'timeZone': 'Japan',
        },
    }
    event = service.events().insert(calendarId='maiko02626@gmail.com',
                                    body=event).execute()
    print(event['id'])

# if __name__ == '__main__':
#     output = get_settle_info(CODE)
#     print('a')
#     result = transform_style(output)
#     print('b')
#     save_file(result, CODE)
#     print('c')
#     main()
