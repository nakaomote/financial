#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Run everything.
"""

from sony import sonyBank
from sony_download import sonyDownload

#sonyBank()

import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
for sonySection in list(map(lambda x: x[5:], filter(lambda x: x.startswith("sony_"), config.sections()))):
    sonyDownload(sonySection)
    sonyBank("YenFutsuRireki.csv", "2021-03-23")
