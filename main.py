# coding = UTF-8
# 爬取自己编写的html链接中的PDF文档,网址：file:///E:/ZjuTH/Documents/pythonCode/pythontest.html

import urllib.request
from urllib import parse
import datetime
import sqlite3
import re
import os

# open the url and read
def getHtml(url):
    try:
        page = urllib.request.urlopen(url)
        html = page.read()
        page.close()
        return html
    except Exception as e:
        print(e)
        return ""

def getNextPage(html):
    reg = r'.*href\=\"(.*)\".*class=\"prevnext\".*'
    url_re = re.compile(reg)
    url_lst = url_re.findall(html.decode('UTF-8'))
    return(url_lst)

def getUrl(html):
    #html = str(html).replace("\n", "")
    reg = r'.*href\=\"(.*)\".*title=\".*class=\"thumbnail\"'
    url_re = re.compile(reg)
    url_lst = url_re.findall(html.decode('UTF-8'))
    return(url_lst)

def getMp4Url(html):
    reg = r'(http:\/\/.*\.mp4).*240p'
    url_re = re.compile(reg)
    url_lst = url_re.findall(html.decode('UTF-8'))
    return(url_lst)

def getFile(url):
    f = ...
    try:
        file_name = url.split('/')[-1]
        u = urllib.request.urlopen(url)
        f = open(file_name, 'wb')

        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            f.write(buffer)
        f.close()
        print ("Sucessful to download" + " " + file_name)
        return file_name
    except Exception as e:
        f.close()
        print("下载时发生错误，跳过此文件的下载 ", file_name)
        if os.path.exists(file_name):
            #删除文件，可使用以下两种方法。
            os.remove(file_name)

        return ''

root_url = 'http://www.aotu43.com'

if not os.path.exists('mp4_download'):
    os.mkdir('mp4_download')

os.chdir(os.path.join(os.getcwd(), 'mp4_download'))

conn = sqlite3.connect('mp4_history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS MP4_DOWNLOAD
         (ID VARCHAR(64) PRIMARY KEY     NOT NULL,
         MP4_URL      TEXT   NOT NULL,
         PAGE_URL     TEXT   NOT NULL,
         PARENT_URL   TEXT   NOT NULL,
         CREAT_TIME   DATETIME );''')

raw_url = root_url
while raw_url :
    print("raw_url = " , raw_url)
    html = getHtml(raw_url)

    if not html:
        continue

    url_lst = getUrl(html)
    # print(url_lst)
    for url in url_lst:
        s = parse.quote(url)
        s = root_url + s
        mp4_html = getHtml(s)

        if not mp4_html:
            continue

        mp4_url_lst = getMp4Url(mp4_html)

        for mp4Url in mp4_url_lst[:]:
            print('   mp4Url=', mp4Url)  #形成完整的下载地址

            file_name = mp4Url.split('/')[-1]

            c.execute("select count(*) from MP4_DOWNLOAD where ID = :id ", {'id':file_name})
            count = c.fetchone()[0]
            if count > 0:
                continue

            fileNm = getFile(mp4Url)
            if fileNm:
                sql = '''insert into MP4_DOWNLOAD (ID, MP4_URL, PAGE_URL, PARENT_URL,CREAT_TIME) values (:id, :mp4_url, :page_url, :raw_url, :ctime)'''
                c.execute(sql, { 'id':fileNm, 'mp4_url':mp4Url, 'page_url':root_url + url, 'raw_url':raw_url, 'ctime':datetime.datetime.now() })
                conn.commit()

    nextPage = getNextPage(html)

    if len(nextPage) > 0 :
        raw_url = root_url + nextPage.pop()
    else:
        raw_url = ""

conn.close()
print("处理完成")