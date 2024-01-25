#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
from datetime import datetime
import hashlib
import sys
from bs4 import BeautifulSoup

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
        return int(self[Row.BALANCE]) + int(self.__rows[1][Row.AMOUNT]) == int(self.__rows[1][Row.BALANCE])
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

f = open("testicles.html", encoding="shift_jis")
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

                row[Row.DATE] = datetime.strptime("2023/"+row[Row.DATE], '%Y/%m/%d').strftime("%D")
                row[Row.BALANCE] = row[Row.BALANCE].replace(",","").replace("\\","")
                row[Row.AMOUNT] = (row[Row.AMOUNT] or row[Row.BALANCE]).replace(",","")

                if not row.checkBalances():
                    sys.stderr.write("Error for balance!\n")
                    sys.exit(-1)

    for row in rows:
        rowWriter.writerow(row.csvRow())

    if printOn:
        break
