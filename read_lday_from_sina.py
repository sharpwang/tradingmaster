# -*- coding: utf-8 -*-
from struct import *
import urllib2
import MySQLdb
import sys
import lxml.html
import gzip
import StringIO

reload(sys) 
sys.setdefaultencoding( "utf-8" ) 

conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()

rows = cur.execute("""select exchange.exchange_code, exchange.location, stock.stock_code from market.exchange, market.stock 
	where exchange.exchange_code = stock.exchange_code and not exists(select 1 from market.lday where
    lday.ymd = 20150205 and exchange.exchange_code = lday.exchange_code and stock.stock_code = lday.stock_code)""")
row = 0
errs = 0
for stock in cur.fetchall():
	row = row + 1
	exchange_code = stock[0]
	location = stock[1]
	stock_code = stock[2]
	print row, "of", rows, ", " , stock_code

	url = "http://hq.sinajs.cn/list=" + location.lower() + stock_code
	#print url
	sock = urllib2.urlopen(url)
	htmlText = sock.read()
	sock.close()
	pList = []
	try:
		pList = htmlText.split(",")
	except:
		continue
	if len(pList) < 10:
		continue
	close0 = int(float(pList[3]) * 100)
	if int(close0) == 0.0:
		continue
	preclose = int(float(pList[2]) * 100)
	open0 = int(float(pList[1]) * 100)
	high0 = int(float(pList[4]) * 100)
	low0 = int(float(pList[5]) * 100)
	if int(low0) == 0.0:
		continue
	volumn = pList[8]
	amount = pList[9]
	ymd = pList[-3].replace("-","")
	
	lday = (exchange_code,stock_code,ymd, open0, high0, low0, close0, amount, volumn, preclose, -1)
	#print lday

	try:
		cur.execute("""replace into lday(exchange_code, stock_code, ymd, open0, high0, low0, close0, amount, volumn, preclose, bar) 
        	values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", lday)
		cur.execute("update lday set bar = bar + 1 where exchange_code = %s and stock_code = %s", (exchange_code, stock_code))
		conn.commit()
	except:
		errs = errs + 1
		print "Err:", errs, stock_code

cur.execute("""update market.lday t0, market.lday t1 set t0.preamount = t1.amount, t0.prevolumn = t1.volumn
where t0.exchange_code = t1.exchange_code and t0.stock_code = t1.stock_code
and t0.bar = 0 and t1.bar = 1""")
conn.commit()
conn.close()