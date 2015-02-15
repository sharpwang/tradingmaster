# -*- coding: utf-8 -*-
from struct import *
import MySQLdb

#conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
conn = MySQLdb.connect(host="115.29.238.220",port=3306,user="root",passwd="do-it-well",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()

rows = cur.execute("""select exchange.exchange_code, exchange.location, stock.stock_code from market.exchange, market.stock 
  where exchange.exchange_code = stock.exchange_code""")
row = 0
directorys = {"SH":"C:\\new_tdx\\vipdoc\\sh\\lday", "SZ":"C:\\new_tdx\\vipdoc\\sz\\lday"}
for stock in cur.fetchall():
  row = row + 1
  exchange_code = stock[0]
  location = stock[1]
  stock_code = stock[2]
  path = directorys[location] + "\\" + location + stock_code + ".day"
  print row, "of", rows, ", " , stock_code

  try:
    fd=file(path,"rb")
    days = []
    buf = fd.read()
    count = len(buf)/32
    k = 0
    preclose = 0
    preamount = 0.0
    prevolumn = 0
    for k in range(0, count):
      j = k * 32
      (ymn, open0, high, low, close, amount, volumn)=unpack("IIIIIfI", buf[j : (j + 28)])

      day = (exchange_code,stock_code,ymn, open0, high, low, close, amount, volumn, preclose, preamount, prevolumn, count - k - 1)
      #print day
      days.append(day)
      preclose = close
      preamount = amount
      prevolumn = volumn



    cur.executemany("""replace into lday(exchange_code, stock_code, ymd, open0, high0, low0, close0, amount, volumn, preclose, preamount, prevolumn, bar) 
        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", days)
    conn.commit()

  except Exception as e:
        print(e)
  finally:
    fd.close;

conn.close()