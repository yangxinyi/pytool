# encoding: utf-8
'''
Created on 2014年8月29日

@author: yangxinyi

@title: 网页爬虫

@description: 通过“努努书坊”小说目录链接，抓取小说内容 分章节放入novel目录中
操作步骤：写入README.txt文件，程序通过解析该文件获得参数

@warning: 操作中需要注意的几点，如下
1、首先确认页面的编码，UTF-8或GBK。抓取后做响应的解码
2、抓取开启后，监控日志，标题是否准确，是否有特殊字符造成的解码异常
3、抓取完成后，查看section.sql文件，确认标题和顺序是否准确
4、抓取完成后，检查页面是否出现明显的异常（如编码问题导致）
5、确认内容无误后，打包！

'''
import urllib2
from BeautifulSoup import BeautifulSoup
from Novel import Book, Section, Chapter
from _codecs import unicode_escape_decode
import os

class Crawler(object):
    def __init__(self, url):
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        response = urllib2.urlopen(req)
        self._soup = BeautifulSoup(response.read().decode('GBK'))
    
    def getSoup(self):
        return self._soup
    
class Readme(object):
    def __init__(self, path):
        self._path = path
        
    def parse(self):
        file_path = os.path.join(self._path, 'README.txt')
        file_obj = open(file_path, 'r')
        dict = {}
        while True :
            line = file_obj.readline()
            if len(line) == 0 :
                break
            attrs = line.split('=')
            dict[attrs[0].strip()] = attrs[1].strip()
        file_obj.close()
        return dict
    
if __name__ == '__main__':
    bookid = 4
    readme_path = 'novel/%d' % (bookid)
    readme_dict = Readme(readme_path).parse()
    sqlid = int(readme_dict['sqlid'])
    sections = []
    url = readme_dict['url']
    rindex = url.rfind('/')
    url_prefix = url[:rindex + 1]
    cata = Crawler(url)
    soup = cata.getSoup()
    center = soup.find(bgcolor='#d4d0c8', align='center')
    for tr in center.findAll('tr'):
        if tr.get('bgcolor') == '#ffffcc':
            section = Section(sqlid, bookid, tr.find('strong').renderContents())
            sections.append(section)
            sqlid = sqlid + 1
        elif tr.get('bgcolor') == '#ffffff':
            for td in tr.findAll('td'):
                if td.find('a'):
                    print td.find('a')
                    chapter_html = Crawler('%s%s' % (url_prefix, td.find('a').get('href')))
                    chapter_content = chapter_html.getSoup().find('td', align = 'left', bgcolor = '#FFFFFF', width = '820').renderContents().replace('<br />\n<br />\r\n', '<br />\n')
                    chapter_title = td.find('a').renderContents().replace('&middot;', '·')
                    section.appendChapter(Chapter(section, chapter_title, chapter_content))
    book = Book(bookid, readme_dict['bookname'], readme_dict['author'], readme_dict['description'], readme_dict['bookcover'], sections)
    book.parse()
                    
                    
    
