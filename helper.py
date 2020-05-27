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
            date_json["data"].append(links)
            print(date_var)
        except:
            pass
    with open ("date.json") as f:
        json.dump(date_json, f)
    
def driver():
    # get_page_links("2015/01/01")
    make_date_json()