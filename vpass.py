#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Reading ANA Visa Credit Card
"""

import csv
import sys
import codecs

if len(sys.argv) != 2:
    print("%s <meisai>" % sys.argv[0])
    sys.exit(1)

class Transactions():
    AMOUNT = 5

    def __init__(self):
        self.__transactions = list()
        self.balance = None
        self.__lastDate = None

    def addTransaction(self, line: list):
        if len(line) == 3:
            return
        length = len(line) - 1
        for index,value in enumerate(line):
            if index != AMOUNT and len(value) > 0:
                break
            if index == length:
                self.balance = int(line[AMOUNT])
                return
        self.__transactions.append(Transaction(line, self))

    def checkBalance(self):
        for transaction in self.__transactions:
            self.balance += transaction.getAmount()
        if self.balance != 0:
            print("Balance does not match: %d" % self.balance)
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
    def __init__(self, line: list, transactions: Transactions):
        self.__setDate(line[0])
        self.__setName(line[1])
        self.__setAmount(line[Transactions.AMOUNT])

    def __setDate(self, date: str):
        if len(date) > 0:
            self.__date = date
            transactions.setLastDate(date)
            return
        self.__date = transactions.getLastDate()

    def __setName(self, name: str):
        self.__name = name

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
