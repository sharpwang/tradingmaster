# -*- coding: utf-8 -*-
from struct import *
import MySQLdb

conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()

rows = cur.execute("""select exchange.exchange_code, exchange.location, stock.stock_code from market.exchange, market.stock 
	where exchange.exchange_code = stock.exchange_code""")
row = 0
stocks = cur.fetchall()
for stock in stocks:
	row = row + 1
  	print row, "of", rows
  	exchange_code = stock[0]
  	stock_code = stock[2]
  	sql = "select ymd, open1, high1, low1, close1 from market.lday where exchange_code = '" + exchange_code + "' and stock_code = '" + stock_code + "'"
  	rows0 = cur.execute(sql)
  	if rows0 == 0:
  		continue

	S = 12
	L = 26
	M = 9
	ema_short = 0.0
	ema_long = 0.0
	dea = 0.0
	premacd = 0.0
	updown = 0
	overzero = 0

	preclose = 0
	zd = 0.0 #涨跌幅
	zf = 0.0 #振幅
	zdt = 0 #涨跌停数目

	upds = []
	ldays = cur.fetchall()
	k = 0
	for lday in ldays:
		ymd = int(lday[0])
		close1 = int(lday[4])
		c = close1 / 100.0
		if k == 0:
			ema_short = c 
			ema_long = c 
		else:
			ema_short = (2 * c  + (S - 1) * ema_short) / (S + 1)
			ema_long = (2 * c  + (L - 1) * ema_long) / (L + 1)
		dif = 0.0 + ema_short - ema_long
		dea = (2 * dif + (M - 1) * dea) / (M + 1)
		macd = (dif - dea) * 2
		if macd > premacd:
			if updown > 0:
				updown = updown + 1
			else:
				updown = 1
		elif macd < premacd:
			if updown < 0:
				updown = updown - 1
			else:
				updown = -1
		else:
			updown = 0

		if macd > 0:
			if overzero > 0:
				overzero = overzero + 1
			else:
				overzero = 1
		elif macd < 0:
			if overzero < 0:
				overzero = overzero - 1
			else:
				overzero = -1
		else:
			overzero = 0

		open1 = int(lday[1])
		high1 = int(lday[2])
		low1 = int(lday[3])
		close1 = int(lday[4])
		if preclose == 0:
			zd = 100.0 * (close1 - open1) / open1
		else:
			zd = 100.0 * (close1 - preclose) / preclose
		zf = 100.0 * (high1 - low1) / low1
		if zd > 9.88 and high1 == close1: #涨停
			if zdt < 0: #从跌停到涨停，重新计算涨跌停数
				zdt = 0
			zdt = zdt + 1
		elif zd < -9.88 and low1 == close1:
			if zdt > 0:
				zdt = 0
			zdt = zdt - 1
		else:
			zdt = 0

		upd = (dif, dea, macd, updown, overzero, preclose, zd, zf, zdt, exchange_code, stock_code, ymd)
		upds.append(upd)
		#print upd
		premacd = macd
		preclose = close1
		k = k + 1

	cur.executemany("""update market.lday set dif = %s, dea = %s, macd = %s, updown = %s, overzero = %s, preclose = %s, zd = %s, zf = %s, zdt = %s 
		where exchange_code = %s and stock_code = %s and ymd = %s""", upds)
	conn.commit()









