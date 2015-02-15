# -*- coding: utf-8 -*-
from struct import *
import urllib2
import MySQLdb
import sys
import re
import os
from email.mime.text import MIMEText  
import traceback
import smtplib

def send_message(recipients, subject, body):
    mailboxs = [{'smtp' : 'smtp.qq.com', 'port' : 587, 'user' : '831261@qq.com', 'pass' : 'miAujv8R', 'tls' : False, 'ssl' : False}, \
    {'smtp' : 'mail.gmx.com', 'port' : 587, 'user' : 'wangzhen@gmx.com', 'pass' : 'miAujv8R', 'tls' : True, 'ssl' : False},  \
    {'smtp' : 'my.inbox.com', 'port' : 465, 'user' : 'wangzhen@inbox.com', 'pass': 'Duv7irYd', 'tls' : False, 'ssl' : True}]
    msg = MIMEText(body,'html','utf-8')
    msg['Subject'] = subject
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

url = "http://xueqiu.com/pearlzou"
request = urllib2.Request(url)
request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36')
sock = urllib2.urlopen(request)
htmlText = sock.read()
sock.close()

htmlText.decode("utf-8","ignore")

pattern = re.compile(r"\"id\"\:(\d{8})\,\"user_id\"\:(1557735636)\,[^\}]*\"description\"\:\"([^\,]*)\"\,\"type\"")

match = pattern.findall(htmlText)
for m in match:
	txtfile = "pearlzou_" + m[0] +".txt"
	if not os.path.exists(txtfile):
		f = open(txtfile, "w")
		txt = ""
		rawTxt = m[2]
		isText = True
		for i in range(len(rawTxt)):
			if rawTxt[i] == '<':
				isText = False
			if isText:
				txt = txt + rawTxt[i]
			if rawTxt[i] == '>':
				isText = True
		txt = txt + "\nhttp://xueqiu.com/1557735636/" + m[0]
		print m[0], txt
		f.write(txt)
		f.close

		recipients = ['831261@qq.com','20891206@qq.com']
		#没有发送过，发送内容到上述地址
		title = '易碎品发新贴了 ' + m[0]
		content = txt
		if send_message(recipients, title, content) == True:
			print 'send a messge to recipients' + title

