# encoding: utf-8
'''
Created on 2014年8月29日

@author: yangxinyi

@title: 网页爬虫

@description: 通过“努努书坊”小说目录链接，抓取小说内容 分章节放入novel目录中

'''
import urllib2
from BeautifulSoup import BeautifulSoup
import os

class Crawler(object):
    def __init__(self, url):
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        response = urllib2.urlopen(req)
        self._soup = BeautifulSoup(response.read())
    
    def getSoup(self):
        return self._soup

class Chapter(object):
    def __init__(self, section, title, text):
        self._section = section
        self._title = title
        self._text = text
    
    def getSection(self):    
        return self._section
        
    def getTitle(self):
        return self._title
    
    def getText(self):
        return self._text

class Section(object):
    def __init__(self, sqlid, title):
        self._id = sqlid
        self._title = title
        self._chapters = []
        
    def getId(self):    
        return self._id
        
    def getTitle(self):
        return self._title
    
    def appendChapter(self, chapter):
        self._chapters.append(chapter)
        
    def getChapters(self):
        return self._chapters

class Parser(object):
    def __init__(self, bookid, sections):
        self._bookid = bookid
        self._sections = sections
        
    def parse(self):
        book_path = 'novel/%d' % (self._bookid)
        if not os.path.exists(book_path):
            os.mkdir(book_path)
        i = 1
        sql_file = open('novel/section.sql', 'w')
        parent_sql_list = []
        item_sql_list = []
        for section in self._sections:
            j = 1
            section_path = 'novel/%d/%d' % (self._bookid, section.getId())
            if not os.path.exists(section_path):
                os.mkdir(section_path)
            parent_sql_list.append('insert into novel_bookitem(id, book_id, name, page_no) values (%d, %d, \'%s\', %d);\n' 
                    % (section.getId(), self._bookid, section.getTitle().encode('utf-8'), i))
            i = i + 1
            for chapter in section.getChapters():
                chapter_path = 'novel/%d/%d/%d.html' % (self._bookid, section.getId(), j)
                item_sql_list.append('insert into novel_bookitem(book_id, parent, name, page_no, path) values (%d, %d, \'%s\', %d, \'%s\');\n' 
                    % (self._bookid, section.getId(), chapter.getTitle().encode('utf-8'), j, chapter_path))
                chapter_file = open(chapter_path, 'w')
                chapter_file.write(chapter.getText().replace('<br />\n<br />\r\n', '<br />\n'))
                chapter_file.close()
                j = j + 1
        sql_file.write(''.join(parent_sql_list))
        sql_file.write(''.join(item_sql_list))
        sql_file.close()
    
if __name__ == '__main__':
    bookid = 1
    sqlid = 230 #通过线上提供接口查询novel_bookitem最大id
    sections = []
    url = 'http://book.kanunu.org/files/xunhuan/200805/561.html'
    rindex = url.rfind('/')
    url_prefix = url[:rindex + 1]
    cata = Crawler(url)
    soup = cata.getSoup()
    center = soup.find(bgcolor='#d4d0c8', align='center')
    for tr in center.findAll('tr'):
        if tr.get('bgcolor') == '#ffffcc':
            section = Section(sqlid, tr.find('strong').renderContents())
            sections.append(section)
            sqlid = sqlid + 1
        elif tr.get('bgcolor') == '#ffffff':
            for td in tr.findAll('td'):
                if td.find('a'):
                    chapter_html = Crawler('%s%s' % (url_prefix, td.find('a').get('href')))
                    chapter_content = chapter_html.getSoup().find('td', align = 'left', bgcolor = '#FFFFFF', width = '820').renderContents()
                    chapter_title = td.find('a').renderContents()
                    section.appendChapter(Chapter(section, chapter_title, chapter_content))
    parser = Parser(bookid, sections)
    parser.parse()
                    
                    
    
