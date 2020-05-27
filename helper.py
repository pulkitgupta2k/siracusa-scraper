import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
from datetime import datetime, date, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import itertools

def getSoup(link):
    req = requests.get(link)
    html = req.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

def jump_by_month(start_date, end_date, month_step=1):
    current_date = start_date
    while current_date < end_date:
        yield current_date
        carry, new_month = divmod(current_date.month - 1 + month_step, 12)
        new_month += 1
        current_date = current_date.replace(year=current_date.year + carry,
                                            month=new_month)

def append_rows(self, values, value_input_option='RAW'):
    params = {
        'valueInputOption': value_input_option
    }
    body = {
        'majorDimension': 'ROWS',
        'values': values
    }
    return self.spreadsheet.values_append(self.title, params, body)

def get_page_links(date):
    link = "https://www.comune.siracusa.it/index.php/it/component/jevents/month.calendar/{}/491".format(date)
    soup = getSoup(link)
    links = []
    soup = soup.findAll("a", {"class": "cal_titlelink"})
    for s in soup:
        link = "https://www.comune.siracusa.it"+s['href']
        links.append(link)
    return links

def make_date_json():
    start_date = date(2015, 1, 1)
    end_date = date.today()
    date_json = {}
    date_json["data"] = []
    for single_date in jump_by_month(start_date, end_date):
        date_var = single_date.strftime("%Y/%m/%d")
        try:
            links = get_page_links(date_var)
            date_json["data"].extend(links)
            print(date_var)
        except:
            pass
    with open ("links.json", "w") as f:
        json.dump(date_json, f)
    
def get_detail(link):
    soup = getSoup(link)
    soup = soup.find("div", {"class": "jev_evdt_desc"}).find("table",{"border": "1"})
    rows = soup.findAll("tr")[1:]
    ret_det = {}
    date_var = link.split("/")
    date_var = "{}/{}/{}".format(date_var[-6], date_var[-5], date_var[-4])
    for row in rows:
        col = row.findAll("td")
        cod = col[0].text.strip()
        desc = col[1].text.strip()
        proven = col[2].text.strip()
        mis = col[3].text.strip()
        cat = col[4].text.strip()
        pre = col[-1].text.strip()
        name = "{}:{}:{}:{}:{}".format(cod, desc, proven, mis, cat)
        ret_det[name] ="{}:{}".format(date_var, pre)
    return ret_det

def get_all_details():
    with open ("links.json") as f:
        links = json.load(f)["data"]
    all_details = {}
    for link in links:
        try:
            details = get_detail(link)
        except:
            continue
        for key_detail, value_detail in details.items():
            if key_detail not in all_details:
                all_details[key_detail] = {}
            date_var = value_detail.split(":")[0]
            pre_var = value_detail.split(":")[1]
            all_details[key_detail][date_var] = pre_var
        print(link)
    with open("details.json", "w") as f:
        json.dump(all_details, f)

def driver():
    get_all_details()