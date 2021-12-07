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
import subprocess
from datetime import datetime

cfg = Config()
core = Core(cfg)

reload(sys)
sys.setdefaultencoding('utf8')

# ============================================================================================
# Секция функций общего назначения


######################################################
#          Секция функции MAIN
######################################################


if os.path.isfile(cfg.pidfile):
    pid = long(open(cfg.pidfile, 'r').read())
    date_start = []
    if core.check_pid(pid):
	dt_check = datetime.now().strftime("%H:%M")
        # try:
        #    date_start = subprocess.check_output('ps -p %s -o etimes' % pid, shell=True).split('\n')
        # except OSError as err:
        #    core.flogger('Error: %s ' % err)
	
        # core.flogger(" proverka %s" % int(date_start[1]))

        # if int(date_start[1]) > 21600:
	core.flogger(" Время запуска - %s" % dt_check)
	if (dt_check > '00:00') and (dt_check < '00:10'):
            subprocess.call("kill -TERM %s" % pid, shell=True)
	    subprocess.call("x=`ps ax | grep -v grep | grep tail | awk '{print $1}'`; kill $x", shell=True)
            core.write_data_in_file('dhcpstats.log', '', cfg.LOGDIR, 'w')
            core.flogger(' ======= перезапуск скрипта ======= ')
            os.unlink(cfg.pidfile)
        else:
            core.flogger('pidfile уже существует' + cfg.pidfile + '. Выход...')
            sys.exit()
    else:
        core.flogger(' ======= Скрипт не запущен. перезапуск скрипта ======= ')
        os.unlink(cfg.pidfile)

core.flogger('======================')
core.flogger(' ===== Начало работы скрипта =====')
pid = str(os.getpid())
open(cfg.pidfile, 'w').write(pid)

#with open(cfg.DhcpLease, 'r') as f:
#    for line in f.readlines():
#        line = line.split(' ')
#        if line[0] == 'lease':
#            l_ip = line[1]
#            for i in cfg.GWNET:
#                maska = "%s/%s" % (i[1], i[2])
#                maska2 = "%s/%s" % (i[3], i[4])
#                if(core.addressInNetwork(l_ip, maska)):
#                    for ii in cfg.GW:
#                        if i[0] == ii[0]:
#                            ii[5] += 1
#                if(core.addressInNetwork(l_ip, maska2)):
#                    for ii in cfg.GW:
#                        if i[0] == ii[0]:
#                            ii[6] += 1
#
#for ia in cfg.GW:
#    print("%s %s %s" % (ia[0], ia[5], ia[6]))
date_update = int(datetime.now().strftime("%s")) + 300
proc = subprocess.Popen(['tail', '-f', cfg.ReadLogDhcp], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
core.flogger('Начало парсинга лог файла')
for line in iter(proc.stdout.readline, ''):
    line = line.split(' ')
    if'DHCPACK' in line:
        ip_komm = line[-1].replace('\n', '')
        # core.write_data_in_file('temp.txt', line, None, 'a')
        for i in cfg.GW:
            if ip_komm == i[1]:
                i[3] += 1
            if ip_komm == i[2]:
                i[4] += 1
            # print("%s %s %s" % (i[0], i[3], i[4]))
    if date_update < int(datetime.now().strftime("%s")):
        BODY = ''
        date_update = int(datetime.now().strftime("%s")) + 300
        for i in cfg.GW:
            x = int(i[3]) + int(i[4])
            BODY += "%s:%s " % (i[0], x)
            i[3] = 0
            i[4] = 0
        core.write_data_in_file('cactidhcp.txt', BODY, None, 'w')
        core.ftp_upload(cfg.TMPDIR, 'cactidhcp.txt')



# ============================================================================================
# finish
core.flogger(' ======= Конец работы скрипта ======= ')
os.unlink(cfg.pidfile)
