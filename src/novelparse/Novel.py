# encoding: utf-8
'''
Created on 2014年8月29日

@author: yangxinyi

@title: 小说三级：书、卷、章节

'''

'''
    章：所在卷、标题、内容
'''
import os

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
    
    def parse(self, path):
        chapter_file = open(path, 'w')
        chapter_file.write(self._text)
        chapter_file.close()

'''
    卷：所在书、指定id，标题、包含的章节列表
'''
class Section(object):
    def __init__(self, sqlid, bookid, title):
        self._id = sqlid
        self._bookid = bookid
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

'''
    书：指定id、书名、作者、描述、封面、包含的卷列表
'''
class Book(object):
    def __init__(self, bookid, bookname, author, description, bookcover, sections):
        self._bookid = bookid
        self._bookname = bookname
        self._author = author
        self._decription = description
        self._bookcover = bookcover
        self._sections = sections
    
    '''
            根据三级结构，解析出书的目录和内容，同时产生对应的数据库插入语句
    '''    
    def parse(self):
        book_path = 'novel/%d' % (self._bookid)
        if not os.path.exists(book_path):
            os.mkdir(book_path)
        i = 1
        sql_path = 'novel/%d/section.sql' % (self._bookid)
        sql_file = open(sql_path, 'w')
        parent_sql_list = []
        item_sql_list = []
        for section in self._sections:
            j = 1
            section_path = 'novel/%d/%d' % (self._bookid, section.getId())
            if not os.path.exists(section_path):
                os.mkdir(section_path)
            parent_sql_list.append('insert into novel_bookitem(id, book_id, name, page_no) values (%d, %d, \'%s\', %d);\n' 
                    % (section.getId(), self._bookid, section.getTitle(), i))
            i = i + 1
            for chapter in section.getChapters():
                chapter_path = 'novel/%d/%d/%d.html' % (self._bookid, section.getId(), j)
                item_sql_list.append('insert into novel_bookitem(book_id, parent, name, page_no, path) values (%d, %d, \'%s\', %d, \'%s\');\n' 
                    % (self._bookid, section.getId(), chapter.getTitle(), j, chapter_path))
                chapter_file = open(chapter_path, 'w')
                chapter_file.write(chapter.getText())
                chapter_file.close()
                j = j + 1
        sql_file.write('insert into novel_book(id, name, author, description, cover) values (%d, \'%s\', \'%s\', \'%s\', \'%s\');\n'
                    % (self._bookid, self._bookname, self._author, self._decription, 'novel/' + str(self._bookid) + '/' + self._bookcover))
        sql_file.write(''.join(parent_sql_list))
        sql_file.write(''.join(item_sql_list))
        sql_file.close()

    