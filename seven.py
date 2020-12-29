#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Seven Bank
"""

import csv
import sys
import codecs
import datetime
import hashlib

if len(sys.argv) == 1:
    print("%s <meisai> <meisai>" % sys.argv[0])
    sys.exit(1)

class BaseTransaction():
    def __init__(self, line: list):

        self.line = line
        self.__setDate()
        self.__setAmount()
        self.__setDescription()

    def _setHash(self):
        m = hashlib.md5()
        m.update(
            self.getDate().encode("utf-8") +
            self.getDescription().encode("utf-8") +
            str(self.getAmount()).encode("utf-8") +
            self.getTxNumber().encode("utf-8")
        )
        self.__hash = m.hexdigest()

    def __setDescription(self):
        self.__description = self.line[2]

    def __setAmount(self):
        self.__amount = 0 - int(line[3].replace(",", ""))

    def __setDate(self):
        self.__date = self.line[1].replace("/", "-")

    def getAmount(self) -> int:
        return self.__amount

    def getTxNumber(self) -> str:
        return self._txnumber

    def getDate(self) -> str:
        return self.__date

    def getHash(self) -> str:
        return self.__hash

    def getDescription(self) -> str:
        return self.__description

class UpdatedTransaction(BaseTransaction):
    def __init__(self, line: list):
        if len(line) != 7:
            raise Exception("Incorrect number of fields")
        super().__init__(line)
        self.__setTxNumber()
        self._setHash()

    def __setTxNumber(self):
        self._txnumber = "+" + self.line[6]

class Transaction(BaseTransaction):
    def __init__(self, line: list):
        if len(line) != 6:
            raise Exception("Incorrect number of fields")
        super().__init__(line)
        self.__setTxNumber()
        self._setHash()

    def __setTxNumber(self):
        self._txnumber = self.line[5]

class Transactions():

    def __init__(self):
        self.__transactions = list()
        self.__mode = None
        self.__categoryHeaders = {
            "◆ご利用明細内訳（お振替済分）": Transaction,
            "◆ご利用明細内訳（差額分・お振替未済分）": UpdatedTransaction,
        }

    def addTransaction(self, line: list):
        if self.__mode is None:
            return
        if line[0].endswith("]のご利用明細内訳（差額・お振替未済分）はございません"):
            return None
        if line[0] == "ご利用者":
            return None
        if len(line) not in [ 6, 7 ]:
            return None
        transaction = self.__mode(line)
        self.__transactions.append(transaction)

    def print(self):
        rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        for transaction in self.__transactions:
            rowWriter.writerow([
                transaction.getHash(),
                transaction.getDate(),
                transaction.getDescription(),
                transaction.getAmount(),
                transaction.getTxNumber(),
            ])

    def checkCategoryHeaders(self, line) -> bool:
        if line[0] in self.__categoryHeaders:
            self.__mode = self.__categoryHeaders[line[0]]
            return True
        return False

transactions = Transactions()
for file in sys.argv[1:]:
    for line in csv.reader(codecs.open(file, "r", "shift_jis")):
        if len(line) == 0 or transactions.checkCategoryHeaders(line):
            continue
        transactions.addTransaction(line)

transactions.print()
