#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Reading ANA Visa Credit Card
"""

import csv
import sys
import codecs

if len(sys.argv) != 3:
    print("%s <meisai> <balance>" % sys.argv[0])
    sys.exit(1)

class Transaction():
    def __init__(self, line: list):
        self.line = line # XXX for debugging

        self.__setDate(line[0])
        self.__setName(line[1])
        self.__setAmount(line[6])

    def __setDate(self, date: str):
        self.__date = date

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

class Transactions():
    def __init__(self):
        self.__transactions = list()

    def addTransaction(self, transaction: Transaction):
        self.__transactions.append(transaction)

    def checkBalance(self, balance: int):
        for transaction in self.__transactions:
            balance += transaction.getAmount()
        if balance != 0:
            print("Balance does not match")
            sys.exit(1)

    def print(self):
        rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        for transaction in self.__transactions:
            rowWriter.writerow([
                transaction.getDate(),
                transaction.getName(),
                transaction.getAmount(),
            ])

transactions = Transactions()
for line in csv.reader(codecs.open(sys.argv[1], "r", "shift_jis")):
    transactions.addTransaction(Transaction(line))

transactions.checkBalance(int(sys.argv[2]))
transactions.print()
