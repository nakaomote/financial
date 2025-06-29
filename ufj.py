#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UFJ
"""

import csv
import sys
import codecs
import hashlib
import os
import glob
from typing import Union

from ufj_download import ufjDownload

def ufjAll(dirname: str):
    from forge import bankRun

    def bankRunGenerator(outputFile: str) -> list[bankRun]:
        def download():
            ufjDownload()

        def getFinalBalance() -> Union[None, int]:
            return None

        def parse():
            downloadFile = glob.glob(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "0019642_*.csv"
                )
            )[0]
            ufjBank(downloadFile)
            os.remove(downloadFile)

        return [bankRun(
            filename=os.path.join(dirname, outputFile),
            download=download,
            parse=parse,
            finalBalance=getFinalBalance,
        )]

    return bankRunGenerator(os.path.join(dirname,"ufj.csv"))

class Transaction():
    def __init__(self, line: list):
        self.line = line
        self.__setDate()
        self.__setBalance()
        self.__setAmount()
        self.__setDescription()
        self.__setHash()

    def __setHash(self):
        m = hashlib.md5()
        m.update(
            self.getDate().encode("utf-8") +
            self.getDescription().encode("utf-8") +
            str(self.getBalance()).encode("utf-8") +
            str(self.getAmount()).encode("utf-8")
        )
        self.__hash = m.hexdigest()

    def __setDescription(self):
        description = self.line[1] + (" " + self.line[2] if len(self.line[2]) > 0 else "")
        self.__description = description

    def __setBalance(self):
        self.__balance = int(self.line[5].replace(",", ""))

    def __setAmount(self):
        if len(self.line[3]) > 0:
            self.__amount = 0 - int(self.line[3].replace(",", ""))
            return
        if len(self.line[4]) > 0:
            self.__amount = int(self.line[4].replace(",", ""))
            return
        print("Something wrong with amounts...")
        sys.exit(1)

    def __setDate(self):
        self.__date = self.line[0].replace("/", "-")

    def getAmount(self) -> int:
        return self.__amount

    def getBalance(self) -> int:
        return self.__balance

    def getDate(self) -> str:
        return self.__date

    def getHash(self) -> str:
        return self.__hash

    def getDescription(self) -> str:
        return self.__description

class Transactions():
    def __init__(self):
        self.__transactions = list()
        self.__balance = None

    def addTransaction(self, transaction: Transaction):
        self.checkBalance(transaction)
        self.__transactions.append(transaction)

    def checkBalance(self, transaction: Transaction):
        if self.__balance is None:
            self.__balance = transaction.getBalance()
            return
        self.__balance += transaction.getAmount()
        if self.__balance != transaction.getBalance():
            print("Balance does not match......")
            print("%d != %d" % (self.__balance, transaction.getBalance()))
            sys.exit(1)

    def print(self):
        rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        for transaction in self.__transactions:
            rowWriter.writerow([
                transaction.getHash(),
                transaction.getDate(),
                transaction.getDescription(),
                transaction.getAmount(),
                transaction.getBalance(),
            ])

def ufjBank(meisai: str):
    transactions = Transactions()
    for line in csv.reader(codecs.open(meisai, "r", "shift_jis")):
        if line[0] != "日付":
            transactions.addTransaction(Transaction(line))

    transactions.print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("%s <meisai>" % sys.argv[0])
        sys.exit(1)

    ufjBank(sys.argv[1])
