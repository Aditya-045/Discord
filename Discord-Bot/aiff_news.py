import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
url = "https://www.the-aiff.com"
html=requests.get(url)
soup = BeautifulSoup(html.content, "html.parser")
pl=soup.find_all("div",{"class":"title"})

def get_news():
    try:
        img=soup.find("div",{"class":"image-cont"})
        img= img.get('style')
        img=img[img.index("(")+1:-1]
    except:
        img='https://www.the-aiff.com/media/uploads/2022/06/ARI_0055-800x500.jpg'
    news={}
    for i in pl:
        try:
            n=i.find("a")
            title=n.get("alt")
            if "<" in title:
                title=title[title.find(">")+1:]
                title=title[:title.find("<")]
            href=n.get("href")
            news[href]=title
        except:
            continue
    return news,img

    
