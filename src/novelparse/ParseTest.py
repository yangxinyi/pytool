# encoding: utf-8

import urllib2
from WebCrawler import Crawler
from Novel import Chapter


if __name__ == '__main__':
    
    req = urllib2.Request('http://book.kanunu.org/files/xunhuan/200805/561/37946.html', headers={'User-Agent' : "Magic Browser"})
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response.read().decode('GBK'))
    print soup.find('td', align = 'left', bgcolor = '#FFFFFF', width = '820')
    chapter_content = soup.find('td', align = 'left', bgcolor = '#FFFFFF', width = '820').renderContents().replace('<br />\n<br />\r\n', '<br />\n')
    Chapter(None, None, chapter_content).parse('novel/1/231/11.html')

