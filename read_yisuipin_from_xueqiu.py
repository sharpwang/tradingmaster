# -*- coding: utf-8 -*-
from struct import *
import urllib2
import MySQLdb
import sys
import re

url = "http://xueqiu.com/pearlzou"
request = urllib2.Request(url)
request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36')
sock = urllib2.urlopen(request)
htmlText = sock.read()
sock.close()

htmlText.decode("utf-8","ignore")
#print htmlText
f = open("pearlzou.html", "w")


pattern = re.compile(r"\"statuses\":\[(\{[\s\S]*\})\]")

match = pattern.findall(htmlText)
for m in match:
	print m
	f.write(m)
f.close()