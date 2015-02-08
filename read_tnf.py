# -*- coding: utf-8 -*-
from struct import *
import MySQLdb
import sys

reload(sys) 
sys.setdefaultencoding( "utf-8" ) 

conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()

fd=file("shm.tnf","rb")

tnfs = []
try:
  buf = fd.read()
  count = (len(buf) - 50)/314
  k = 0

  for k in range(0, count):
  	j = 50 + k * 314
  	(code, dummy1, name0, dummy2, py, dummy3)=unpack("6s17s8s254s8s21s", buf[j : (j + 314)])
  	name = name0.decode("gbk")
  	name = name.split('\0', 1)[0]
  	py = py.split('\0', 1)[0]
  	prefix = code[:2]
  	id_exchange = 0
  	if prefix == "60":
  		id_exchange =  1
  	elif prefix == "00":
  		id_exchange = 2
  		if code[2] == '2':
  			id_exchange = 3
  	elif prefix == "30":
  		id_exchange = 4
  	if id_exchange > 0:
  		tnf = (id_exchange, code, name, py)
  		tnfs.append(tnf)
finally:
  fd.close;

cur.executemany("""insert into stock(id_exchange, name, code, py) 
      values(%s, %s, %s, %s)""", tnfs)
conn.commit()
#  finally:
conn.close()