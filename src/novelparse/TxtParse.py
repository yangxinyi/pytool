# encoding: utf-8
'''
Created on 2014年8月29日

@author: yangxinyi

@summary: 本地txt文件解析。此方式已暂停使用，暂作技术储备

@warning: 解析功能没有调试完成，但思路是完整的。
'''
import re
import MySQLdb
import os

class NovelItem(object):

    def __init__(self, bookid, parentid, name, pageno, path):
        self._bookid = bookid
        self._parentid = parentid
        self._name = name
        self._pageno = pageno
        self._path = path

class NovelParser(object):

    def __init__(self, fileobj, head, parent, bookname):
        self._name = bookname #书名
        self._head = head  #系列编号
        self._parent = parent  #系列编号对应数据库id
        self._file = fileobj #文件对象
        self._items = []  #insert语句数据
    
    def read(self):
        n = 0
        blank_match = re.compile(r'^[\s]*\n')
        title_match = re.compile(ur'^(\u7b2c[\u4e00-\u9fa5]+\u7ae0)\s*\u3000*([\u4e00-\uff09]+)$')#\uff09
        
        curfile = None;
        while True :
            line = self._file.readline()
            if len(line) == 0 :
                if curfile:
                    curfile.close()
                break
            if blank_match.match(line):
                continue
            line = line.strip().decode('utf8')
            title = title_match.match(line)
            if title:
                n += 1
                if curfile:
                    curfile.close()
                curfile = open('novel/' + str(self._head) + '_' + str(self._parent) + '_' + str(n) + '.html', 'w')
                curfile.write((u'<h3>%s<span>%s</span></h3>\n' % (title.group(1), title.group(2))).encode('utf-8'))
                self._items.append(NovelItem(self._head, self._parent, title.group(1) + ' ' + title.group(2), n, u'novel/%d/%d/%d.html' % (self._head, self._parent, n)))
            else:
                curfile.write((u'%s<br />\n' % line).encode('utf-8'))
        return self._items
    
    def execute(self):
        conn = MySQLdb.connect('localhost', 'root', 'root', 'myfood', 3306)
        conn.set_character_set('utf8')
        cur = conn.cursor()
        
        cur.execute(u'insert into novel_note(parent, name, page_no) values (%d, \'%s\', %s);' % (2, self._name, self._head))
        self._parent = cur.lastrowid
        
        self.read()
        if len(self._insertsqls) > 0 :
            for insert_sql in self._insertsqls:
                conn.cursor().execute(insert_sql)
            conn.commit()
        
        cur.close()
        conn.close()   
    
if __name__ == '__main__':
    # import sys
    head = 2
    parent = 3
    bookname = u'权利的游戏'
    bookpath = u'2_权利的游戏.txt'
    if os.path.exists(bookpath): 
        filename = bookpath
        fileobject = open(bookpath, 'r')
        novel = NovelParser(fileobject, head, parent, bookname)
        for novelItem in novel.read():
            print novelItem._path
        fileobject.close()
       
        
