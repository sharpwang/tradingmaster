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

rows = cur.execute("select exchange.exchange_code, exchange.location, stock.stock_code from market.exchange, market.stock where exchange.exchange_code = stock.exchange_code order by stock.stock_code")
row = 0
for stock in cur.fetchall():
 	row = row + 1
 	exchange_code = stock[0]
  	stock_code = stock[2]
  	print stock_code, ",", row, "of", rows
	url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/" + stock_code + ".phtml"
	sock = urllib2.urlopen(url)
	htmlText = sock.read()
	sock.close()

	htmlText.decode("gbk")

	bouns = {}
	doc = lxml.html.fromstring(htmlText)
	trList = doc.xpath(u'//*[@id="sharebonus_1"]/tbody/tr')
	for tr in trList:
		if len(tr) < 5:
			continue
		td1 = tr[1].text #送股
		td2 = tr[2].text #转增
		td3 = tr[3].text #派息
		td5 = tr[5].text.replace("-","") #除权日
		if len(td5) < 8: #不分配
			continue
		bouns[td5] = (exchange_code, stock_code, td5, td1, td2, td3, "0.0", "0.0")

	trList = doc.xpath(u'//*[@id="sharebonus_2"]/tbody/tr')
	for tr in trList:
		if len(tr) < 5:
			continue
		td1 = tr[1].text #配股数
		td2 = tr[2].text #配股价
		td4 = tr[4].text.replace("-","") #除权日
		if len(td4) < 8:
			continue
		b = bouns.get(td4)
		if b == None:
			bouns[td4] = (exchange_code, stock_code, td4, "0.0", "0.0", "0.0", td1, td2)
		else:
			l = list(b)
			l[4] = td1
			l[5] = td2
			b = tuple(l)
			bouns[td4] = b

	for k, v in bouns.items():
		print v
		cur.execute("""replace into sharebouns(exchange_code, stock_code, ymd, song, zeng, pai, pei, ppei) 
	        values(%s, %s, %s, %s, %s, %s, %s, %s)""", v)
		conn.commit()
conn.close()