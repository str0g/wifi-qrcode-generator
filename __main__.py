#!/bin/usr/python

from optparse import OptionParser
from os.path import expanduser
from io import BytesIO
from subprocess import Popen, PIPE
from shutil import copyfile
import json
import base64
import tempfile
import os

import qrcode

#pip install qrcode pillow

FORMAT = '''\
WIFI:T:{security_standard};S:{ssid};P:{password};H:{hidden};\
'''

OUTFILE_TEX = 'out.tex'
OUTFILE_PDF = OUTFILE_TEX.replace('.tex', '.pdf')


def get_profile(path:str):
    with open(path) as fd:
        cfg = json.load(fd)
    return FORMAT.format(**cfg), cfg


def get_qrcode(data: str):
    qr = qrcode.make(data)
    io = BytesIO()
    qr.save('test_qr.png')
    qr.save(io, format='png')
    io.seek(0)
    b64 = base64.b64encode(io.getvalue()).decode('utf-8')
    return {'qrcode': b64}


def get_template(path:str):
    with open(path) as fd:
        return fd.read()


def build(data: str):
    with tempfile.TemporaryDirectory() as tmpdirname:
        print('created temporary directory', tmpdirname)
        current_dir = os.getcwd()
        os.chdir(tmpdirname)
        with open(OUTFILE_TEX, 'w') as fd:
            fd.write(data)

        with Popen(['pdflatex', '--shell-escape', OUTFILE_TEX], stdout=PIPE) as proc:
            out = proc.stdout.read().decode('utf-8').split('\n')
        # @TODO verbose
        #print('\n'.join(out))
        os.chdir(current_dir)
        copyfile(os.path.join(tmpdirname, OUTFILE_PDF), OUTFILE_PDF)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i", "--input", type="string",
                      default="config.json",
                      help="Configuration file")
    parser.add_option("-t", "--template", type="string",
                      default="template.tex",
                      help="Output template")
    #
    (options, args) = parser.parse_args()
    if options.input.find('~') != -1:
        options.input = expanduser(options.input)
    if options.template.find('~') != -1:
        options.template = expanduser(options.template)
    #
    profile, cfg = get_profile(options.input)

    out = {}
    out.update(cfg)
    out.update(get_qrcode(profile))

    template = get_template(options.template).format(**out)
    build(template)

    print(f'Created {OUTFILE_PDF}')
