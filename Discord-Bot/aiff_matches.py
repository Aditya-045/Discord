import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import date,timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_matchreport():
    global day
    global months
    global matches
    global venue
    from datetime import date
    global match_date
    global today
    global d1
    global m1
    global d2
    today=date.today()
    d1,m1=today.strftime("%d"),today.strftime("%b")
    yest=today-timedelta(days=1)
    d2=yest.strftime("%d")
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.the-aiff.com"
    #driver = webdriver.Firefox(executable_path=".\\geckodriver.exe")
    driver.get(url)
    time.sleep(15)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    day=[]
    months=[]
    matches=[]
    date=soup.find_all("div",{"class":"match_date"})
    for d in date:
        day.append(int(d.text.strip()))
    month=soup.find_all("div",{"class":"day-month"})
    for d in month:
        months.append(d.text.strip()[-10:].strip())
    match_date=list(zip(day,months))
    c=1
    score= soup.find_all("div",{"class":"lower-cont"})
    for sc in score:
        try:
            venue= sc.find("div",{"class":"venue"}).text.strip()
        except:
            pass
        try:
            clubs=[n.text.strip() for n in sc.find_all("div",{"class":"team-name text-center"})]
        except:
            pass
        try:
            score= sc.find("div",{"class":"table-div full eq-wid"}).text.strip()
            if ":" in score:
                score=score+" IST "
        except:
            pass
        lst=[clubs[0],score,clubs[1]]
        matches.append(lst)
    driver.close()

def match_today():
    get_matchreport()
    global day
    global months
    global matches
    global venue
    global match_date
    global today
    global d1
    global m1
    mtday=[]
    for i,f in list(zip(match_date,matches)):
        if int(i[0])==int(d1):
            mtday.append([i,f])
    return mtday
def match_yest():
    global day
    global months
    global matches
    global venue
    global match_date
    global today
    global date
    global d1
    global m1
    mtday=[]
    for i,f in zip(match_date,matches):
        if int(i[0])==int(d2):
            mtday.append([i,f])
    return mtday
