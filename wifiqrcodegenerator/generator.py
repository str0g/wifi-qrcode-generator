#!/usr/bin/python

# -*- coding: utf-8 -*-

#################################################################################
#    wifi-qrcode-generator is a program to automate sharing user and password   #
#    for any wifi network                                                       #
#    Copyright (C) 2021  Łukasz Buśko                                           #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU General Public License as published by       #
#    the Free Software Foundation, either version 2 of the License, or          #
#    (at your option) any later version.                                        #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU General Public License for more details.                               #
#                                                                               #
#    You should have received a copy of the GNU General Public License          #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#################################################################################

from io import BytesIO
import shutil
import base64
import tempfile
import os
import stat
import subprocess
import logging

import qrcode

logger = logging.getLogger('wifi-qrcode-generator')
OUTFILE_TEX = 'out.tex'
OUTFILE_PDF = OUTFILE_TEX.replace('.tex', '.pdf')


class Generator:
    SPECIAL = ['&', '%', '$' ,'#' ,'_' ,'{', '}', '~', '^' ,'\\']
    FORMAT = '''\
WIFI:T:{security_standard};S:{ssid};P:{password};H:{hidden};\
'''
    SECURITY_STANDARDS = ['WPA', 'WEP', '']
    HIDDEN = ['true', '']

    def __init__(self, ssid: str, passwd: str, template: str, security_standard:str = 'WPA', hidden: str =''):
        if not security_standard in self.SECURITY_STANDARDS:
            raise ValueError(f'Unknown security standard {security_standard} choose from {self.SECURITY_STANDARDS}')
        if not hidden in self.HIDDEN:
            raise ValueError(f'Wrong hidden value choose from {self.HIDDEN}')

        qrcode_string = f'WIFI:T:{security_standard};S:{ssid};P:{passwd};H:{hidden};'
        template_dict = {
            'ssid': self.replace_special(ssid),
            'password': self.replace_special(passwd),
            'qrcode': self.get_qrcode(qrcode_string),
        }
        self.template = template.format(**template_dict)
        logger.debug(self.template)

        self.path = ssid

    def replace_special(self, data: str):
        check = list(data)
        return ''.join([f'\\{c}' if c in self.SPECIAL else c for c in check])

    def get_qrcode(self, data: str):
        qr = qrcode.make(data)
        io = BytesIO()
        if logger.level == logging.DEBUG:
            qr.save(OUTFILE_TEX.replace('.tex', '.png'))
        qr.save(io, format='png')
        io.seek(0)
        b64 = base64.b64encode(io.getvalue()).decode('utf-8')
        return b64

    def set_permissions(self, path: str, permissions=stat.S_IRUSR|stat.S_IWUSR):
        os.chmod(path, permissions)

    def save_file(self, filepath: str = OUTFILE_PDF, timeout: int = 1):
        with tempfile.TemporaryDirectory() as tmpdirname:
            logger.debug(f'created temporary directory {tmpdirname}')

            out_tex = os.path.join(tmpdirname, OUTFILE_TEX)
            logger.debug(f'writing to {out_tex}')
            with open(out_tex, 'w') as fd:
                fd.write(self.template)

            logger.debug('executing build with pdflatex')
            tmp_pdf = os.path.join(tmpdirname, OUTFILE_PDF)
            try:
                proc = subprocess.run(['pdflatex', '--shell-escape', OUTFILE_TEX], stdout=subprocess.PIPE, timeout=timeout,
                            cwd=tmpdirname)
                proc.check_returncode()
                self.set_permissions(tmp_pdf)
                logger.debug(proc.stdout.decode('utf-8'))
                shutil.move(tmp_pdf, filepath)
                return True
            except subprocess.TimeoutExpired as e:
                logger.warning(proc.stdout.decode('utf-8'))
                logger.warning(e)
            except subprocess.CalledProcessError as e:
                logger.warning(proc.stdout.decode('utf-8'))
                logger.warning(e)
        return False