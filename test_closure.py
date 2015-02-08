# -*- coding: utf-8 -*- 
from struct import *
import MySQLdb
import math

conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()

capital = 500000.00
start_day = 20140901
end_day = 20141231
current_day = start_day
holdings = []
vcapital = capital
force_sell = False
while True:
	for i in range(len(holdings)):
		position = holdings[i]
		enter_day, exchange_code, stock_code, enter_price, volumn = position
		if volumn > 0:
			rows = cur.execute("select close1, updown from market.lday where exchange_code = %s and stock_code = %s and ymd = %s", (exchange_code, stock_code, current_day))
			if rows == 0:
				continue
			close1, updown = cur.fetchone()
			exit_price = int(close1)
			if force_sell or int(updown) < 0 or 100.0*exit_price/enter_price < 95.0:
				position[4] = 0
				capital = capital + volumn * exit_price
				profit = volumn * (exit_price - enter_price)
				vcapital = vcapital + profit
				#print capital, "S", current_day, stock_code, exit_price, volumn
				holdings[i] = position
	print vcapital, current_day
	if force_sell:
		break
	rows = cur.execute("""
	select stock.exchange_code,stock.stock_code,stock.name, lday0.ymd, lday0.bar, lday0.open1
	from market.stock stock, market.lday lday0
	where stock.exchange_code=lday0.exchange_code and stock.stock_code=lday0.stock_code
  		and lday0.ymd =  %s and exists( select 1 from market.lday lday1 where 
        lday0.exchange_code = lday1.exchange_code and lday0.stock_code = lday1.stock_code
        and lday1.rzdt = 2 and lday1.bar = lday0.bar + 1)
  	""", (current_day,))
  	#print current_day, rows
	if rows > 0:
		pools = cur.fetchall()
		capital1 = capital / rows
		for target in pools:
			exchange_code, stock_code, stock_name, ymd, bar, open1 = target
			enter_price = int(open1)
			volumn = math.floor(capital1 / enter_price)
			if(volumn > 0):
				position = [current_day, exchange_code, stock_code, enter_price, volumn]
				holdings.append(position)
				capital = capital - volumn * enter_price
				#print capital, "B", current_day, stock_code, enter_price, volumn
	nextday = cur.execute("select min(ymd) from market.lday where ymd > %s and ymd <= %s", (current_day, end_day))
	row = cur.fetchone()
	if row[0] == None:
		force_sell = True
	else:
		current_day = int(row[0])


