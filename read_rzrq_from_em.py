# -*- coding: utf-8 -*-
from struct import *
import urllib2
import MySQLdb
import sys
import re
import os
import matplotlib.pyplot as plt
import smtplib
import traceback
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 

reload(sys) 
sys.setdefaultencoding( "utf-8" ) 

def send_message(recipients, msg):
	mailboxs = [{'smtp' : 'smtp.qq.com', 'port' : 587, 'user' : '831261@qq.com', 'pass' : 'Mu8LonZa', 'tls' : False, 'ssl' : False}, \
	{'smtp' : 'mail.gmx.com', 'port' : 587, 'user' : 'wangzhen@gmx.com', 'pass' : 'miAujv8R', 'tls' : True, 'ssl' : False},  \
	{'smtp' : 'my.inbox.com', 'port' : 465, 'user' : 'wangzhen@inbox.com', 'pass': 'Duv7irYd', 'tls' : False, 'ssl' : True}]
	for mailbox in mailboxs:
		smtpserver = mailbox['smtp']
		port = mailbox['port']
		sender = mailbox['user']
		password = mailbox['pass']
		try:
			smtp_connect = lambda ssl, server: smtplib.SMTP_SSL(server) if ssl else smtplib.SMTP(server)
			smtp = smtp_connect(mailbox['ssl'],smtpserver)
			smtp.set_debuglevel(1)
			if mailbox['tls'] == True:
				smtp.ehlo()
				smtp.starttls()
				smtp.ehlo()
			smtp.login(sender, password)
			smtp.sendmail(sender, recipients, msg.as_string())
			smtp.quit()
			#print "send mail using " + sender + " succeed"
			return True
		except Exception, e:
			traceback.print_exc()
			print "send mail using " + sender + " failed"
			continue
	return False


conn = MySQLdb.connect(host="localhost",port=3307,user="root",passwd="333333",db="market",charset="utf8",use_unicode=True )
cur=conn.cursor()

url = "http://data.eastmoney.com/rzrq/total.html"
#http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=FD&sty=SHSZHSSUM&st=0&sr=1&p=2&ps=50&js=var%20KXINBOXI={pages:(pc),data:[(x)]}&rt=47446752
	#print url
sock = urllib2.urlopen(url)
htmlText = sock.read()
htmlText.decode("gbk")
#print htmlText
sock.close()

pattern = re.compile(r"\"(\d{4}-\d{2}-\d{2},\d*,\d*,\d*,\d*,\d*,\d*,\d*,\d*,\d*,\d*,\d*,\d*)\"")


rzrq = []
match = pattern.findall(htmlText)
for m in match:
	t = m.replace("-","")
	l = t.split(",")
	rzrq.append(tuple(l))

cur.executemany("""replace into twoloan(ymd, shrzy, szrzy, hsrzy, shrz, szrz, hsrz, shrqy, szrqy, hsrqy, shrzrqy, szrzrqy, hsrzrqy)
	values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", rzrq)
conn.commit()

rets = cur.execute("select ymd, hsrzrqy/100000000 from market.twoloan order by ymd desc limit 0,60")
ymds = []
loans = []
rows = cur.fetchall()
for row in rows:
	ymd = str(row[0])[-4:]
	ymds.insert(0, ymd)
	loan = float(row[1])
	loans.insert(0, loan)
#print loans
cur.close()
conn.close()

dpi = 72.0
xinch = 1136 / dpi
yinch = 640 / dpi
axescolor  = '#f6f6f6'
fig = plt.figure(figsize=(xinch,yinch), dpi=dpi)
ax = fig.add_subplot(1, 1, 1)
tick_no=[0, 9, 19, 29, 39, 49, 59]
ax.set_xticks(tick_no)
ticks = [ymds[i] for i in tick_no]
ax.set_xticklabels(ticks)
ax.plot(loans,color='r',linestyle='-',marker='o')
plt.grid(True)
imgfiles = "twoloan" + ymds[-1] +".png"
if not os.path.exists(imgfiles):
	plt.savefig(imgfiles)

	subject = '市场两融余额走势图' + ymds[-1]
	msg = MIMEMultipart()
	msg['Subject'] = subject
	#msg['To'] = '831261@qq.com'
	#msg['From'] = '831261@qq.com'

	# 邮件内容
	Contents = MIMEText('','html', 'utf-8')
	msg.attach(Contents)

	# 带上二进制附件  
	att = MIMEImage(file(imgfiles, 'rb').read())
	att["Content-Type"] = 'application/octet-stream'  
	att.add_header('content-disposition','attachment',filename=imgfiles)
	msg.attach(att)

	recipients = ['831261@qq.com']
	if send_message(recipients, msg) == True:
		print "Send Msg OK!"
