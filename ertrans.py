# -*- coding: utf-8 -*-
f1 = open('__ER__.txt', 'r')
f2 = open('ER.txt', 'w')

while True:
	line = f1.readline()
	if not line:
		break
	line1 = line.decode("utf8")
	pos = line1.find(u"【")
	if pos != -1:
		line1 = line1[pos:]
	pos = line1.find(u":00")
	if pos != -1: 
		line1 = line1[:pos]
	line2 = line1 + "\n\n"
	line = line2.encode("utf8")
	f2.write(line)
f1.close()
f2.close()
