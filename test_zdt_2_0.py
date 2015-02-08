# -*- coding: utf-8 -*- 
from struct import *
import MySQLdb
import math
#测试双涨停最原始的版本。效果不理想。满仓操作。如果已经买入，第二天碰见其他标的将无法再次购买。
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
"""
500000.0 20140901
500000.0 20140902
500000.0 20140903
492620.0 20140904
476844.0 20140905
492262.0 20140909
498116.0 20140910
506450.0 20140911
498810.0 20140912
494963.0 20140915
485912.0 20140916
474000.0 20140917
491246.0 20140918
499307.0 20140919
484326.0 20140922
514461.0 20140923
525134.0 20140924
514983.0 20140925
508925.0 20140926
509805.0 20140929
505801.0 20140930
502845.0 20141008
495312.0 20141009
495312.0 20141010
495312.0 20141013
500284.0 20141014
522802.0 20141015
522802.0 20141016
500344.0 20141017
498463.0 20141020
457090.0 20141021
411040.0 20141022
411040.0 20141023
409410.0 20141024
409410.0 20141027
396162.0 20141028
396162.0 20141029
396162.0 20141030
411534.0 20141031
411534.0 20141103
411534.0 20141104
458863.0 20141105
485043.0 20141106
454478.0 20141107
454478.0 20141110
457832.0 20141111
457832.0 20141112
468330.0 20141113
459094.0 20141114
414736.0 20141117
407136.0 20141118
419649.0 20141119
419751.0 20141120
397729.0 20141121
397729.0 20141124
385502.0 20141125
385502.0 20141126
383812.0 20141127
395280.0 20141128
392519.0 20141201
403243.0 20141202
421919.0 20141203
420213.0 20141204
416743.0 20141205
419809.0 20141208
449729.0 20141209
441719.0 20141210
442489.0 20141211
449729.0 20141212
438012.0 20141215
408462.0 20141216
403879.0 20141217
404149.0 20141218
403383.0 20141219
416774.0 20141222
372088.0 20141223
386357.0 20141224
386207.0 20141225
384185.0 20141226
355515.0 20141229
356719.0 20141230
356719.0 20141231
380094.0 20141231
[Finished in 277.9s]
"""