#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
CSV download
"""

import requests
import configparser
import os
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
settings = config['sony']

session = requests.Session()
session.get("https://o2o.moneykit.net/NBG100001G01.html?nc=181029001")

post = {
	"LoginKS": "",
	"__type": "0003",
	"__gid": "NBP000109G01",
	"__sid": "",
	"__uid": "7166197",
	"__fid": "NBP000109",
	"B_ID": "1",
	"DirectId": "",
	"ExParam": "",
	"TenNo": settings["tenno"],
	"KozaNo": settings["kozano"],
	"Password": settings["pass"]
}

r = session.post("https://o2o.moneykit.net/TDGate1/gate/NBW000010", post)
soup = BeautifulSoup(r.text, 'html.parser')
inputs = soup.select('input')

post = { input["name"]: input["value"] for input in inputs }

session.post("https://o2o.moneykit.net/TDGate010300/gate/NBW010300/&NBPO2OTMPG01", post)

post = {
	"LoginKS": "1",
	"__type": "0023",
	"__uid": "0017166197",
	"__sid": post["__sid"],
	"__gid": "NBP010105G01",
	"__fid": "NBP010116",
	"B_ID": "001",
	"TenNo": "001",
	"KozaNo": "7166197",
	"CsvStartTime": "1900/01/01+00:00:00",
    "CsvEndTime": datetime.now(timezone("Asia/Tokyo")).strftime("%Y/%m/%d+23:59:59")
}

r = session.post("https://o2o.moneykit.net/TDGate000036/gate/NBW000036/YenFutsuRireki.csv", post)
with open("sony.csv", "w") as rb:
    rb.write(r.text)
