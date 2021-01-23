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

from optparse import OptionParser
from os.path import expanduser
import json
import logging

from wifiqrcodegenerator import Generator

logger = logging.getLogger('example')


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


def get_profile(path: str):
    with open(path) as fd:
        cfg = json.load(fd)
    logger.debug('profile loaded, filling qrcode template')
    return cfg


def get_template(path:str):
    with open(path) as fd:
        return fd.read()


def set_logger(verbose: bool):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)


if __name__ == "__main__":
    (options, args) = get_options()
    set_logger(options.verbose)

    cfg = get_profile(options.input)
    template = get_template(options.template)

    gen = Generator(cfg['ssid'], cfg['password'], template)
    outfile = f"{cfg['ssid']}.pdf"
    if gen.save_file(outfile):
        logger.info(f'Created {outfile}')
    else:
        logger.warning(f'Something went wrong during {outfile} creation')
