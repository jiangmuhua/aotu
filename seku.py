# coding = UTF-8
# 爬取自己编写的html链接中的MP4文档
import urllib.request
import time
from urllib import parse
from datetime import datetime as dt
#import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
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
        log(e)
        return ""

# 获取下一页
def getMaxPage(html):
    soup = BeautifulSoup(html, 'html.parser')
    url_lst = soup.select('div.pagination > div.pagination-holder > ul > li.last > a')
    if len(url_lst) > 0:
        url = url_lst.pop();
        page = url['href'].split('/')[-2];
        if page:
            return int(page)
        else:
            return 0
    else:
        return 0

# 获取网页链接
def getUrl(html):
    soup = BeautifulSoup(html, 'html.parser')
    url_lst = soup.select('div.list-videos > div.margin-fix > div.item > a')
    return(url_lst)

# 获取MP4文件链接
def getMp4Url(html):
    reg = r'(http:\/\/.*\.mp4).*240p'
    url_re = re.compile(reg)
    url_lst = url_re.findall(html.decode('UTF-8'))
    return(url_lst)

# 下载文件
def getFile(url):
    f = ...
    try:
        file_name = url.split('/')[-2]
        u = urllib.request.urlopen(url)
        meta = u.info()
        file_size = int(meta["Content-Length"])
        f = open(file_name, 'wb')
        block_sz = 8192
        log("下载文件 {0} SIZE={1}M ".format(file_name, round(file_size / 1024 / 1024, 2)));
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            f.write(buffer)
            f.flush()

        f.close()

        log("下载文件成功 " + file_name)
        return file_name
    except Exception as e:
        #print(e)
        f.close()
        log("下载失败，跳过此文件的下载 " + file_name)
        if os.path.exists(file_name):
            #删除文件，可使用以下两种方法。
            os.remove(file_name)
        return ''

def log(msg):
    print(dt.now().strftime("%Y-%m-%d %H:%M:%S") + " "+ msg)

if __name__ == '__main__':

    # 判断是否存在下载目录，如果不存在，创建
    if not os.path.exists('seku_download'):
        os.mkdir('seku_download')

    # 进入目录
    os.chdir(os.path.join(os.getcwd(), 'seku_download'))

    root_url = 'http://seku.tv/latest-updates/{0}/'
    log("为爱而生 for seku. 请稍后……")

    #display = Display(visible=0, size=(800, 600))
    #display.start()
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    try:
        maxPage = 2
        for pageIdx in range(1, maxPage):
            log("开始处理PAGE={0}数据".format(pageIdx))
            raw_url = root_url.format(pageIdx)
            html = getHtml(raw_url)
            if not html:
                continue

            if pageIdx == 1:
                maxPage = getMaxPage(html)

            url_lst = getUrl(html)
            for url in url_lst:
                str = url['href']
                log("正在处理网页:" + str)
                browser = webdriver.Chrome(executable_path='../chromedriver.exe',chrome_options=chrome_options)
                #browser = webdriver.Chrome('../chromedriver.exe')
                #browser.set_window_size(200, 200)
                browser.get(str)
                time.sleep(5)
                fpUi = browser.find_elements_by_class_name("fp-ui")
                if len(fpUi) == 0:
                    continue

                fpUi[0].click()
                time.sleep(5)
                fpUi[0].click()
                mp4Url = browser.find_element_by_tag_name("video").get_attribute('src')
                browser.quit()
                #browser.close()
                if not mp4Url:
                    continue
                log("成功获取视频地址:" + mp4Url)
                # 获取文件名
                file_name = mp4Url.split('/')[-2]
                if os.path.exists(file_name):
                    log("下载文件{0}已经存在，跳过处理".format(file_name))
                    continue

                # 下载文件，如果下载成功则保存下载记录到数据库
                fileNm = getFile(mp4Url)
        # 循环处理结束
        log("处理完成")
    except KeyboardInterrupt:
        log("任务被取消")
   # finally:
     #   display.stop()
