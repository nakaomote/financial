#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Sony Bank
"""

import csv
import sys
import codecs
import datetime
import hashlib
from descriptions import Descriptions
import configparser
import os
from sony_download import sonyDownload

def sonyAll(dirname: str):
    from forge import bankRun

    downloadFile = "YenFutsuRireki.csv"

    def bankRunGenerator(sonySection: str) -> bankRun:
        finalFile = f"sony-{sonySection}.csv"

        def download():
            sonyDownload(sonySection)

        def parse():
            sonyBank(downloadFile, "2021-03-23")
            os.remove(downloadFile)

        return bankRun(
            filename=os.path.join(dirname, finalFile),
            download=download,
            parse=parse,
        )

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
    return list(map(lambda x: bankRunGenerator(x[5:]), filter(lambda x: x.startswith("sony_"), config.sections())))

def sonyBank(meisai: str, startDate: str):
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
                str(self.getBalance()).encode("utf-8") +
                str(self.getAmount()).encode("utf-8")
            )
            self.__hash = m.hexdigest()

        def __setDescription(self):
            description = line[1]
            if line[1].startswith("Visaデビット"):
                description = description[16:-1]
            self.__description = Descriptions().getName(description)

        def __setBalance(self):
            self.__balance = int(line[5].replace(",", ""))

        def __setAmount(self):
            if len(line[4]) > 0:
                self.__amount = 0 - int(line[4].replace(",", ""))
                return
            if len(line[3]) > 0:
                self.__amount = int(line[3].replace(",", ""))
                return
            print("Something wrong with amounts...")
            sys.exit(1)

        def __setDate(self):
            date = self.line[0]
            for rep in ("年", "月"):
                date = date.replace(rep, "-")
            self.__date = date.replace("日", "")

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

        def getDateTimestamp(self) -> int:
            return int(datetime.datetime.strptime(self.getDate(), "%Y-%m-%d").strftime("%s"))

    class Transactions():
        def __init__(self, startDate):
            self.__startDate = int(datetime.datetime.strptime(startDate, "%Y-%m-%d").strftime("%s"))
            self.__transactions = list()
            self.__balance = None

        def addTransaction(self, transaction: Transaction):
            if (transaction.getDateTimestamp() > self.__startDate):
                self.checkBalance(transaction)
                self.__transactions.append(transaction)

        def checkBalance(self, transaction: Transaction):
            if self.__balance is None:
                self.__balance = transaction.getBalance()
                return
            self.__balance += transaction.getAmount()
            if self.__balance != transaction.getBalance():
                print("Balance does not match......")
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

    transactions = Transactions(startDate)
    for line in csv.reader(codecs.open(meisai, "r")):
        if line[0] != "お取り引き日":
            transactions.addTransaction(Transaction(line))

    transactions.print()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("%s <meisai> <start-date>" % sys.argv[0])
        sys.exit(1)

    sonyBank(sys.argv[1], sys.argv[2])
