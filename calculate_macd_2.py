# -*- coding: utf-8 -*- 
from struct import *
import MySQLdb
import math

def calc_volality():
	listzf = []
	def __volality(close1, preclose):
		if preclose == 0:
			preclose = close1
		lnzf = 	math.log((close1 + 0.0)/preclose)
		#print close1, preclose, lnzf
		listzf.append(lnzf)
		if len(listzf) < 21:
			return 0.0
		sum0 = 0.0
		for i in range(20):
			j = -1 - i
			sum0 = sum0 + listzf[j]
		avg0 = sum0 / 20
		sum1 = 0.0
		for i in range(20):
			j = -1 - i
			mean2 = listzf[j] - avg0
			sum1 = sum1 + mean2 * mean2
		ret0 = math.sqrt(sum1 / 20) * 1587.4507866
		return ret0
	return __volality



def calc_zdzf2():
	listzdzf = []
	def __zdzf2(zd, zf):
		zdzf = math.sqrt(zd * zd + zf * zf)
		#print close1, preclose, lnzf
		listzdzf.append(zdzf)
		avg0 = avg1 = 0.0
		sum0 = sum1 = 0.0
		if len(listzdzf) < 5:
			return avg0, avg1
		for i in range(5):
			j = -1 - i
			sum0 = sum0 + listzdzf[j]
			avg0 = sum0 / 5.0
		if len(listzdzf) < 21:
			return avg0, avg1
		for i in range(20):
			j = -1 - i
			sum1 = sum1 + listzdzf[j]
		avg1 = sum1 / 20.0
		sum1 = 0.0
		return avg0, avg1
	return __zdzf2


def calc_zdt():
	indicator = {"rzdt":0, "zdt":0, "preclose":0}
	def __zdt(open1, high1, low1, close1):
		preclose = indicator["preclose"]
		zdt = indicator["zdt"]
		rzdt = indicator["rzdt"]
		if preclose == 0:
			zd = 100.0 * (close1 - open1) / open1
		else:
			zd = 100.0 * (close1 - preclose) / preclose
		zf = 100.0 * (high1 - low1) / low1
		if zd > 9.88 and high1 == close1: #涨停
			if zdt < 0: #从跌停到涨停，重新计算涨跌停数
				zdt = 0
				rzdt = 0

			zdt = zdt + 1
			rzdt = rzdt + 1
			if zf == 0.0: #振幅为0，重新计算真实涨跌停
				rzdt = 0
		elif zd < -9.88 and low1 == close1:
			if zdt > 0:
				zdt = 0
				rzdt = 0
			zdt = zdt - 1
			rzdt = rzdt - 1
			if zf == 0.0:
				rzdt = 0
		else:
			zdt = 0
			rzdt = 0
		indicator["rzdt"] = rzdt
		indicator["zdt"] = zdt
		indicator["preclose"] = close1
		return zd, zf, zdt, rzdt
	return __zdt



def calc_macd():
	S = 12
	L = 26
	M = 9
	indicator = {"ema_short":0.0, "ema_long":0.0, "dea":0.0, "premacd":0.0, "updown":0, "overzero":0}
	def __macd(close1):
		ema_short = indicator["ema_short"]
		ema_long = indicator["ema_long"]
		dea = indicator["dea"]
		premacd = indicator["premacd"]
		updown = indicator["updown"]
		overzero = indicator["overzero"]
		c = close1 / 100.0
		if ema_short == 0.0 and ema_long == 0.0:
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
		indicator["ema_short"] = ema_short
		indicator["ema_long"] = ema_long
		indicator["dea"] = dea
		indicator["premacd"] = macd
		indicator["updown"] = updown
		indicator["overzero"] = overzero
		return dif, dea, macd, updown, overzero
	return __macd


conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()
sp_return = cur.execute("call market.sp_recalc_with_bouns()")
rows = cur.execute("""select exchange.exchange_code, exchange.location, stock.stock_code from market.exchange, market.stock 
	where exchange.exchange_code = stock.exchange_code""")
row = 0
stocks = cur.fetchall()
for stock in stocks:
	row = row + 1
  	exchange_code = stock[0]
  	stock_code = stock[2]
  	print stock_code, "|", row, "of", rows
  	sql = "select ymd, open1, high1, low1, close1 from market.lday where exchange_code = '" + exchange_code + "' and stock_code = '" + stock_code + "'"
  	rows0 = cur.execute(sql)
  	if rows0 == 0:
  		continue

  	preclose = 0
  	_volality = calc_volality()
   	_zdt = calc_zdt()
  	_macd = calc_macd()
  	_zdzf2 = calc_zdzf2()
	upds = []
	ldays = cur.fetchall()

	for lday in ldays:
		#print lday
		ymd = int(lday[0])
		open1 = int(lday[1])
		high1 = int(lday[2])
		low1 = int(lday[3])
		close1 = int(lday[4])

		zd, zf, zdt, rzdt = _zdt(open1, high1, low1, close1)
		dif, dea, macd, updown, overzero = _macd(close1)
		vola = _volality(close1, preclose)
		zdzf5, zdzf20 = _zdzf2(zd, zf)

		upd = (dif, dea, macd, updown, overzero, preclose, zd, zf, zdt, rzdt, vola, zdzf5, zdzf20, exchange_code, stock_code, ymd)
		upds.append(upd)
		#print upd
		preclose = close1

	cur.executemany("""update market.lday set dif = %s, dea = %s, macd = %s, updown = %s, overzero = %s, preclose = %s, 
		zd = %s, zf = %s, zdt = %s, rzdt = %s, volality = %s, zdzf5 = %s, zdzf20 = %s
		where exchange_code = %s and stock_code = %s and ymd = %s""", upds)
	conn.commit()
