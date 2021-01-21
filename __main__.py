#!/usr/bin/python

from optparse import OptionParser
from os.path import expanduser
from io import BytesIO
from shutil import copyfile
import json
import base64
import tempfile
import os
import logging
import subprocess

import qrcode

#pip install qrcode pillow

FORMAT = '''\
WIFI:T:{security_standard};S:{ssid};P:{password};H:{hidden};\
'''

OUTFILE_TEX = 'out.tex'
OUTFILE_PDF = OUTFILE_TEX.replace('.tex', '.pdf')
logger = logging.getLogger('wifi-qrcode-generator')


def get_profile(path: str):
    with open(path) as fd:
        cfg = json.load(fd)
    logger.debug('profile loaded, filling qrcode template')
    return FORMAT.format(**cfg), cfg


def get_qrcode(data: str, verbose: bool):
    qr = qrcode.make(data)
    io = BytesIO()
    if verbose:
        qr.save(OUTFILE_TEX.replace('.tex', '.png'))
    qr.save(io, format='png')
    io.seek(0)
    b64 = base64.b64encode(io.getvalue()).decode('utf-8')
    return {'qrcode': b64}


def get_template(path:str):
    with open(path) as fd:
        return fd.read()


def build(data: str):
    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.debug(f'created temporary directory {tmpdirname}')

        out_tex = os.path.join(tmpdirname, OUTFILE_TEX)
        logger.debug(f'writing to {out_tex}')
        with open(out_tex, 'w') as fd:
            fd.write(data)

        logger.debug('executing build with pdflatex')
        try:
            proc = subprocess.run(['pdflatex', '--shell-escape', OUTFILE_TEX], stdout=subprocess.PIPE, timeout=1,
                            cwd=tmpdirname)
            proc.check_returncode()
            logger.debug(proc.stdout.decode('utf-8'))
        except subprocess.TimeoutExpired as e:
            logger.warning(proc.stdout.decode('utf-8'))
            logger.warning(e)
        except subprocess.CalledProcessError as e:
            logger.warning(proc.stdout.decode('utf-8'))
            logger.warning(e)

        logger.debug(out)
        copyfile(os.path.join(tmpdirname, OUTFILE_PDF), OUTFILE_PDF)


def replace_special(data: str):
    special = ['&', '%', '$' ,'#' ,'_' ,'{', '}', '~', '^' ,'\\']
    check = list(data)
    return ''.join([f'\\{c}' if c in special else c for c in check])


def get_options():
    parser = OptionParser()
    parser.add_option("-i", "--input", type="string",
                      default="config.json",
                      help="Configuration file")
    parser.add_option("-t", "--template", type="string",
                      default="template.tex",
                      help="Output template")
    parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose",
                      help="Verbose")

    (options, args) = parser.parse_args()
    if options.input.find('~') != -1:
        options.input = expanduser(options.input)
    if options.template.find('~') != -1:
        options.template = expanduser(options.template)

    return options, args


def set_logger(verbose: bool):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)


if __name__ == "__main__":
    #
    (options, args) = get_options()
    set_logger(options.verbose)
    #
    profile, cfg = get_profile(options.input)
    #
    logger.debug('making things with special characters')
    cfg['ssid'] = replace_special(cfg['ssid'])
    cfg['password'] = replace_special(cfg['password'])

    out = {}
    out.update(cfg)
    out.update(get_qrcode(profile, options.verbose))
    logger.debug('data for template has been prepared')
    logger.debug(out)

    template = get_template(options.template).format(**out)
    logger.debug(template)
    build(template)

    logger.info(f'Created {OUTFILE_PDF}')
