#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# @Author: arex
# @Date:   2018-09-03 09:35:54
# @Last Modified by:   arex
# @Last Modified time: 2018-09-03 17:38:38

import os
import sys
# Подключаем классы
from config import Config
from core import Core
import time
from datetime import datetime
from datetime import timedelta

cfg = Config()
core = Core(cfg)

reload(sys)
sys.setdefaultencoding('utf8')

# ============================================================================================
# Секция функций общего назначения


######################################################
#          Секция функции MAIN
######################################################


if os.path.isfile(cfg.pidfile2):
    pid = long(open(cfg.pidfile2, 'r').read())
    if core.check_pid(pid):
        core.flogger('pidfile уже существует' + cfg.pidfile2 + '. Выход...')
        sys.exit()

core.flogger('======================')
core.flogger(' ===== Начало работы скрипта Total =====')
pid = str(os.getpid())
open(cfg.pidfile2, 'w').write(pid)

# чтение файла dhcpd.leases. парсинг ипэшников и заполнение общего количества
# with open(cfg.DhcpLease, 'r') as f:
leases = open(cfg.DhcpLease, 'r').read().split("}\n")
# for lease in f.read().split("}\n"):
ip_addrs = []
ip_addrs_dbl = []
core.write_data_in_file('temmp.txt', '', None, 'w')
core.write_data_in_file('temmp111.txt', '', None, 'w')
core.write_data_in_file('temmp-activ-date.txt', '', None, 'w')
core.write_data_in_file('temmp-activ-date-menshe.txt', '', None, 'w')
for lease in leases:
    if (lease.split(' ')[0] == 'lease'):
        ip_addr = lease.split('lease')[1].split(' ')[1]
        # ends = lease.split('ends ')[1].split(';')[0].split(' ')
        # date_end = "%s %s" % (ends[1].replace('/', '-'), ends[2])
        # date_end = time.strptime(lease.split('ends ')[1].split(';')[0][2:], "%Y/%m/%d %H:%M:%S")
	# date_end = "%s %s" % (ends[1], ends[2])
	date_end = lease.split('ends ')[1].split(';')[0][2:]
	date_now = datetime.now() - timedelta(hours = 4)
	date_now = date_now.strftime("%Y/%m/%d %H:%M:%S")
	bind_state = lease.split('binding state ')[1].split(';')[0]
        if (date_end > date_now) and (bind_state == 'active'):
            # core.write_data_in_file('temmp-activ-date.txt', lease.replace('\n', ''), None, 'a')
            if ip_addr not in ip_addrs:
                ip_addrs.append(ip_addr)
        	for i in cfg.GWNET:
        	    maska = "%s/%s" % (i[1], i[2])
        	    maska2 = "%s/%s" % (i[3], i[4])
        	    if(core.addressInNetwork(ip_addr, maska)):
        	        for ii in cfg.GW:
        	            if i[0] == ii[0]:
            	                ii[5] += 1
        	    if(core.addressInNetwork(ip_addr, maska2)):
            	        for ii in cfg.GW:
                	    if i[0] == ii[0]:
                    	        ii[6] += 1
            else:
                ip_addrs_dbl.append(ip_addr)
                # core.write_data_in_file('temmp111.txt', ip_addr, None, 'a')
        elif (date_end < date_now) and (bind_state == 'active'):
            pass
            # core.write_data_in_file('temmp-activ-date-menshe.txt', lease.replace('\n', ''), None, 'a')
        #    core.write_data_in_file('temmp123.txt', ip_addr, None, 'a')
# print(len(ip_addrs_dbl))    
BODY = ''
BODY2 = ''
testt = 0
testt2 = 0
for ia in cfg.GW:
    BODY += "%s:%s " % (ia[0], ia[5])
    BODY2 += "%s:%s " % (ia[0], ia[6])
    testt += ia[5]
    testt2 += ia[6]
# print("%s / %s" % (testt, testt2))
BODY3 = "tvtotal:%s inettotal:%s" % (testt, testt2)
core.write_data_in_file('dhcptotaltv.txt', BODY, None)
core.write_data_in_file('dhcptotalpppoe.txt', BODY2, None)
core.write_data_in_file('dhcptotalip.txt', BODY3, None)
core.ftp_upload(cfg.TMPDIR, 'dhcptotaltv.txt')
core.ftp_upload(cfg.TMPDIR, 'dhcptotalpppoe.txt')
core.ftp_upload(cfg.TMPDIR, 'dhcptotalip.txt')

# ============================================================================================
# finish
core.flogger(' ======= Конец работы скрипта Total ======= ')
os.unlink(cfg.pidfile2)
