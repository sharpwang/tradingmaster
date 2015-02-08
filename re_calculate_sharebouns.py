# -*- coding: utf-8 -*-
from struct import *
import MySQLdb

conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()

rows = cur.execute("select exchange.code, exchange.location, stock.code from market.exchange, market.stock where exchange.code = stock.exchange_code and stock.code='000002'")
for stock in cur.fetchall():
	exchange_code = stock[0]
 	stock_code = stock[2]

	sql = "select exchange_code, stock_code, ymd, song, zeng, pai, pei, ppei from sharebonus where exchange_code = " + exchange_code + " and stock_code = " + stock_code + " order by ymd desc"
	rows0 = cur.execute()

	
