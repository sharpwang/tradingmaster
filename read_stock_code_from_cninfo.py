# -*- coding: utf-8 -*-
from struct import *
import urllib2
import MySQLdb
import sys
import lxml.html

reload(sys) 
sys.setdefaultencoding( "utf-8" ) 

conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()

urls = [("SZMB","http://www.cninfo.com.cn/information/sz/mb/szmblclist.html"), 
		("SZSME","http://www.cninfo.com.cn/information/sz/sme/szsmelclist.html"),
		("SZCN","http://www.cninfo.com.cn/information/sz/cn/szcnlclist.html"),
		("SHMB","http://www.cninfo.com.cn/information/sh/mb/shmblclist.html")]

for i in xrange(len(urls)):
	sock = urllib2.urlopen(urls[i][1])
	htmlText = sock.read()
	sock.close()

	htmlText.decode("gbk")

	doc = lxml.html.fromstring(htmlText)
	aList = doc.xpath(u'//td/a')

	for a in aList:
		text =  a.text
		code = text[0:6]
		if code[0] == '9': #不需要B股
			continue
		name = text[7:]
		cur.execute("replace into stock(exchange_code, stock_code, name) values(%s, %s, %s)", (urls[i][0], code, name))
	conn.commit()


#print htmlText

