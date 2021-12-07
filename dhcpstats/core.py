#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# @Author: arex
# @Date:   2018-09-03 10:05:12
# @Last Modified by:   arex
# @Last Modified time: 2018-09-03 17:36:47

import os
import shutil
from datetime import datetime
import logging
import zipfile
import smtplib
import ftplib
#from netaddr import IPNetwork, IPAddress
import socket
import struct

class Core():
    """ класс core для функций"""

    def __init__(self, config):
        """Constructor"""
        self.cfg = config
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=logging.INFO, filename=self.cfg.LogMain)

    def addressInNetwork(self, ip, net):
        """ Входит ли ip в маску сети """
        ipaddr = int(''.join([ '%02x' % int(x) for x in ip.split('.') ]), 16)
        netstr, bits = net.split('/')
        netaddr = int(''.join([ '%02x' % int(x) for x in netstr.split('.') ]), 16)
        mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
	# print("%s - %s" % (ip, netaddr))
	return (ipaddr & mask) == (netaddr & mask)
#         ipaddr = struct.unpack('L', socket.inet_aton(ip))[0]
#         netaddr, bits = net.split('/')
#         netmask = struct.unpack('L', socket.inet_aton(netaddr))[0] & ((2L << int(bits) - 1) - 1)
#         return ipaddr & netmask == netmask

#    def IpInNetwork(self, ip, net):
#        """ Входит ли ip в маску сети """
#        if IPAddress(ip) in IPNetwork(net):
#            return True
#        else:
#            return False

    def flogger(self, log_string, tipo='info'):
        """ ф-я логирования """
        logger = logging.getLogger(__name__)
        if(tipo == 'info'):
            logger.info(log_string)
        elif(tipo == 'err'):
            logger.error(log_string)
        elif(tipo == 'war'):
            logger.warning(log_string)
        return True

    def file_copy(self, in_file, out_file, out_path, dtnow=False, archive=False):
        """ ф-я копирования файлов """
        try:
            if archive is True:
                # shutil.copy(str(in_file), str(out_file))
                if(dtnow):
                    filename = "%s/%s-%s.zip" % (out_path, os.path.splitext(out_file)[0], datetime.now().strftime("%Y-%m-%d_%H:%M"))
                else:
                    filename = "%s/%s.zip" % (out_path, os.path.splitext(out_file)[0])
                f_zip = zipfile.ZipFile(filename, 'w')
                f_zip.write(in_file, compress_type=zipfile.ZIP_DEFLATED)
                f_zip.close()
                # os.remove(out_file)
            else:
                if(dtnow):
                    shutil.copy(str(in_file), "%s/%s-%s.%s" % (out_path, os.path.splitext(out_file)[0], datetime.now().strftime("%Y-%m-%d_%H:%M"), os.path.splitext(out_file)[1]))
                else:
                    shutil.copy(str(in_file), out_path + "/" + str(out_file))
        except OSError as Err:
            self.flogger.error('ошибка копирования файла: %s' % (in_file, out_file, Err))
            return False
        else:
            return True

    def check_pid(self, pid):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def send_email(self, TO, e_body, s_subject):
        """ Функции для email """
        if s_subject is None:
            s_subject = self.cfg.SUBJECT
        BODY = "\r\n".join(['From: %s' % self.cfg.FROM,
                            'To: %s' % TO,
                            'Subject: %s' % s_subject,
                            '', e_body])
        smtpObj = smtplib.SMTP(self.cfg.HOST, 25)
        smtpObj.starttls()
        smtpObj.login(self.cfg.ELogin, self.cfg.EPass)
        try:
            self.flogger('Отправка почты: %s' % BODY)
            smtpObj.sendmail(self.cfg.FROM, TO, BODY.encode(encoding='utf8'))
        except Warning:
            self.flogger('ошибка отправки почты: %s' % BODY, 'err')
        smtpObj.quit()
        return True

    def func_testpath(self, testpath):
        """ Проверяет наличие файла или папки. возвращает: 1 - файл, 2 - папка, 0 - не найден"""
        if os.path.exists(testpath):
            if os.path.isfile(testpath):
                # print('ФАЙЛ')
                # print('Размер:', os.path.getsize(testpath) // 1024, 'Кб')
                # print('Дата создания:', datetime.fromtimestamp(
                #    int(os.path.getctime(testpath))))
                # print('Дата последнего открытия:', datetime.fromtimestamp(
                #     int(os.path.getatime(testpath))))
                # print('Дата последнего изменения:', datetime.fromtimestamp(
                #     int(os.path.getmtime(testpath))))
                self.flogger('ФАЙЛ найден: %s' % testpath, 'info')
                return 1
            elif os.path.isdir(testpath):
                # print('КАТАЛОГ')
                # print('Список объектов в нем: ', os.listdir(testpath))
                self.flogger('Это КАТАЛОГ: %s' % testpath)
                return 2
        else:
            # print('Объект не найден')
            self.flogger('файл не найден: %s' % testpath)
            return 0

    def write_data_in_file(self, file_name, data, path, xzc='w'):
        if path is None:
            path = self.cfg.TMPDIR
        self.flogger('Запись файла: %s/%s' % (path, file_name))
        """ Write data to spec file """
        with open(path + "/" + file_name, xzc) as f:
            f.write("%s\n" % data)
        return 0

    def ftp_upload(self, path, filename):
        self.flogger('Отправка файла на фтп: %s' % filename)
        session = ftplib.FTP( self.cfg.ftp_server_ip, self.cfg.ftp_user, self.cfg.ftp_password)
        file = open("%s/%s" % (path, filename), 'rb')                   # file to send
        session.storbinary('STOR %s' % filename, file)                  # send the file
        file.close()                                                    # close file and FTP
        session.quit()
