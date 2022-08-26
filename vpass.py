#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Reading ANA Visa Credit Card
"""

import csv
import sys
import codecs
from descriptions import Descriptions

if len(sys.argv) != 3:
    print("%s <meisai> <balance>" % sys.argv[0])
    sys.exit(1)


class Transactions():
    #AMOUNT = 5 # August's payment (8th Month)
    AMOUNT = 6 # September's payment (9th Month)

    def __init__(self):
        self.__transactions = list()
        self.__lastDate = None

    def addTransaction(self, line: list):
        if len(line) == 3:
            return
        for index, value in enumerate(line):
            if index != Transactions.AMOUNT and len(value) > 0:
                break
        self.__transactions.append(Transaction(line))

    def checkBalance(self):
        startingBalance = balance = int(sys.argv[2].replace(",",""))
        for transaction in self.__transactions:
            balance += transaction.getAmount()
        if balance != 0:
            print(
                "Balance does not match: %d != %d" % (
                    balance, startingBalance)
            )
            sys.exit(1)

    def setLastDate(self, date: str):
        self.__lastDate = date

    def getLastDate(self) -> str:
        return self.__lastDate

    def print(self):
        rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        for transaction in self.__transactions:
            rowWriter.writerow([
                transaction.getDate(),
                transaction.getName(),
                transaction.getAmount(),
            ])


class Transaction():
    def __init__(self, line: list):
        self.__setDate(line[0])
        self.__setName(line[1])
        try:
            self.__setAmount(line[Transactions.AMOUNT])
        except ValueError:
            sys.stderr.write("Value error for Amount: %d: %s\n" % (Transactions.AMOUNT, line[Transactions.AMOUNT]))
            sys.stderr.write(str(line) + "\n")
            sys.exit(1)

    def __setDate(self, date: str):
        if len(date) > 0:
            self.__date = date
            transactions.setLastDate(date)
            return
        self.__date = transactions.getLastDate()

    def __setName(self, name: str):
        self.__name = Descriptions().getName(name)

    def __setAmount(self, amount: str):
        self.__amount = 0 - int(amount)

    def getDate(self) -> str:
        return self.__date

    def getName(self) -> str:
        return self.__name

    def getAmount(self) -> int:
        return self.__amount


transactions = Transactions()
for line in csv.reader(codecs.open(sys.argv[1], "r", "shift_jis")):
    transactions.addTransaction(line)

transactions.checkBalance()
transactions.print()
