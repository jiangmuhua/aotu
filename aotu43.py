# coding = UTF-8
# 爬取自己编写的html链接中的MP4文档
import urllib.request
from urllib import parse
from datetime import datetime as dt
#import sqlite3
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
def getNextPage(html, root_url):
    reg = r'.*href\=\"(.*)\".*class=\"prevnext\".*'
    url_re = re.compile(reg)
    url_lst = url_re.findall(html.decode('UTF-8'))

    if len(url_lst) > 0:
        return root_url + url_lst.pop()
    else:
        return ""

# 获取网页链接
def getUrl(html):
    #html = str(html).replace("\n", "")
    reg = r'.*href\=\"(.*)\".*title=\".*class=\"thumbnail\"'
    url_re = re.compile(reg)
    url_lst = url_re.findall(html.decode('UTF-8'))
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
        file_name = url.split('/')[-1]
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
    if not os.path.exists('mp4_download'):
        os.mkdir('mp4_download')

    # 进入目录
    os.chdir(os.path.join(os.getcwd(), 'mp4_download'))

    root_url = 'http://www.aotu43.com'
    log("为爱而生 for aotu43. 请稍后……")

    # 判断数据库是否操作并打开，不存在就创建
    # conn = sqlite3.connect('mp4_history.db')
    # cur = conn.cursor()
    # cur.execute('''CREATE TABLE IF NOT EXISTS MP4_DOWNLOAD
    #          (ID VARCHAR(64) PRIMARY KEY     NOT NULL,
    #          MP4_URL      TEXT   NOT NULL,
    #          PAGE_URL     TEXT   NOT NULL,
    #          PARENT_URL   TEXT   NOT NULL,
    #          CREAT_TIME   DATETIME );''')
    # 删除所有数据
    # cur.execute('''DELETE FROM MP4_DOWNLOAD;''')

    raw_url = root_url
    try:
        while raw_url :
            #print("raw_url = " , raw_url)
            html = getHtml(raw_url)

            if not html:
                continue

            url_lst = getUrl(html)
            # print(url_lst)
            for url in url_lst:
                s = root_url + parse.quote(url)
                mp4_html = getHtml(s)

                if not mp4_html:
                    continue

                # 获取MP4文件Url列表
                mp4_url_lst = getMp4Url(mp4_html)
                for mp4Url in mp4_url_lst[:]:

                    # 获取文件名
                    file_name = mp4Url.split('/')[-1]
                    if os.path.exists(file_name):
                        log("下载文件{0}已经存在，跳过处理".format(file_name))
                        continue

                    # 判断文件是否已经被下载过，如果已经下载过则跳过
                    # cur.execute("select count(*) from MP4_DOWNLOAD where ID = :id ", {'id':file_name})
                    # count = cur.fetchone()[0]
                    # if count > 0:
                    #     continue

                    # 下载文件，如果下载成功则保存下载记录到数据库
                    fileNm = getFile(mp4Url)
                    # if fileNm:
                    #     sql = '''insert into MP4_DOWNLOAD (ID, MP4_URL, PAGE_URL, PARENT_URL,CREAT_TIME) values (:id, :mp4_url, :page_url, :raw_url, :ctime)'''
                    #     cur.execute(sql, { 'id':fileNm, 'mp4_url':mp4Url, 'page_url':root_url + url, 'raw_url':raw_url, 'ctime':dt.now() })
                    #     conn.commit()

            # 获取下一页
            raw_url = getNextPage(html, root_url)

        # 循环处理结束
        log("处理完成")
    except KeyboardInterrupt:
        log("任务被取消")
    #finally:
        # conn.close()
