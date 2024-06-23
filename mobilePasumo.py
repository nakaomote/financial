#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
from datetime import datetime
import hashlib
import sys
from bs4 import BeautifulSoup
import configparser
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Column(str):
    def inform(self, columns):
        columns.append(self)

class Row(list):
    DATE = 0
    BALANCE = 5
    AMOUNT = 6

    def inform(self, rows):
        rows.insert(0,self)
        self.__rows = rows

    def checkBalances(self) -> bool:
        if len(self.__rows) < 2:
            return True
        print(self.__rows[1])
        print(self[Row.BALANCE])
        return int(self[Row.BALANCE]) + int(self.__rows[1][Row.AMOUNT]) == int(self.__rows[1][Row.BALANCE].replace("¥",""))
    def makeTransactionId(self):

        m = hashlib.md5()
        m.update(
            self[Row.DATE].encode("utf-8") +
            self[Row.BALANCE].encode("utf-8") +
            self[Row.AMOUNT].encode("utf-8")
        )
        return m.hexdigest()

    def csvRow(self):
        return (
            self.makeTransactionId(),
            self[Row.DATE],
            " ".join([self[1], self[2], self[3], self[4], ]),
            self[Row.AMOUNT],
            self[Row.BALANCE]
        )

if datetime.now().strftime("%Y") != "2024":
    print("Time to check on the year problem, it's not 2024")
    sys.exit(-1)

options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument('--disable-dev-shm-usage')
# XXX TODO
#options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--remote-debugging-port=4444")
options.add_experimental_option("prefs", {
    "download.default_directory": os.path.join(os.environ["HOME"], "work/financial"),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1
})
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.mobile.pasmo.jp/")

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
settings = config['mobilePasumo']

driver.execute_script("arguments[0].value = '" + settings["user"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "MailAddress"))))
driver.execute_script("arguments[0].value = '" + settings["pass"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "Password"))))

WebDriverWait(driver, 180).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "img[src='/img/btn_riyourireki_off.gif']"))).click()

WebDriverWait(driver, 180).until(EC.element_to_be_clickable((By.NAME, "RETURNMENU")))

from io import StringIO
f = StringIO(driver.page_source)
soup = BeautifulSoup(f, 'html.parser')
lst = soup.find_all('table')

rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
rowWriter.writerow(("Txn ID", "Date", "Name", "Amount", "Balance"))
for table in lst:
    printOn = False
    rows: list[Row] = list()
    for row in table.find_all("tr"):
        columns = row.find_all("td")
        if columns[Row.DATE].text == "月/日":
            printOn = True
            continue
        if printOn:
            if len(columns) == 7:
                row = Row()
                row.inform(rows)
                while columns:
                    Column(columns.pop(0).text).inform(row)

                row[Row.DATE] = datetime.strptime("2024/"+row[Row.DATE], '%Y/%m/%d').strftime("%D")
                row[Row.BALANCE] = row[Row.BALANCE].replace("¥","").replace(",","").replace("\\","")
                row[Row.AMOUNT] = (row[Row.AMOUNT] or row[Row.BALANCE]).replace(",","")

                if not row.checkBalances():
                    sys.stderr.write("Error for balance!\n")
                    sys.exit(-1)

    for row in rows:
        rowWriter.writerow(row.csvRow())

    if printOn:
        break
