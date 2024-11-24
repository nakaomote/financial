#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
PayPay Bank
"""

import csv
import codecs
import sys
import datetime
import hashlib
import os
import glob
from descriptions import Descriptions
from jnb_download import jnbDownload

def jnbAll(dirname: str):
    from forge import bankRun

    def bankRunGenerator(outputFile: str) -> list[bankRun]:
        def download():
            jnbDownload()

        def parse():
            files = glob.glob(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "NBG*"
                )
            )
            jnbBank("2024", "10", "1", files)
            for file in files:
                os.remove(file)

        return [bankRun(
            filename=os.path.join(dirname, outputFile),
            download=download,
            parse=parse,
        )]

    return bankRunGenerator(os.path.join(dirname,"jnb.csv"))

class Transaction():
    """
    Transaction
    """
    def __init__(self, transactions: 'Transactions', line: list):
        line.reverse()
        self.__line = line
        self.__amount = 0
        self.__transactions = transactions
        getattr(self, transactions.mode())(line)

    def setHash(self):
        m = hashlib.md5()
        m.update(
            self.getDate().encode("utf-8") +
            str(self.getBalance()).encode("utf-8") +
            str(self.getAmount()).encode("utf-8")
        )
        self.__hash = m.hexdigest()

    def getHash(self) -> str:
        return self.__hash

    def getDate(self) -> str:
        return self.__date

    def __setDate(self):
        self.__date = \
            datetime.datetime.strptime("%d%02d%02d" % (
                int(self.__line.pop()), int(self.__line.pop()), int(self.__line.pop())
            ), '%Y%m%d').strftime("%Y/%m/%d")

    def __setDescription(self):
        self.__description = Descriptions().getName(self.__line.pop())

    def __setReplaceDescription(self):
        self.__description = self.__line.pop().replace("\u3000", " ")

    def __setDebitAmount(self):
        self.__debitAmount = self.__line.pop()

    def __setAmount(self):
        self.__amount -= int(self.__line[-1]) if len(self.__line[-2]) == 0 else (0 - int(self.__line[-2]))
        self.__popCount(2)

    def getAmount(self):
        return self.__amount

    def __setBalance(self):
        self.__balance = int(self.__line.pop())
        self.__transactions.setLastBalance(self)

    def setBalance(self, balance):
        self.__balance = balance

    def getBalance(self) -> int:
        return self.__balance

    def getDescription(self) -> str:
        return self.__description

    def __popAZeroOrElse(self):
        if self.__line.pop() != "0":
            print("Ok we should be 0... but we're not...")
            sys.exit(1)

    def __popValueInTitleOrElse(self, *values):
        if not self.__line.pop() in values:
            print("We should have values: %s" % ",".join(values))
            sys.exit(1)

    def __popCount(self, count: int):
        for i in range(0, count):
            self.__line.pop()

    def __setDebitID(self):
        self.__debitID = self.__line.pop()
        self.__transactions.setDebit(self)

    def getDebitID(self):
        return self.__debitID

    def __emptyOrElse(self):
        if len(self.__line.pop()) != 0:
            print("Non-empty value when it should be empty...")
            sys.exit(1)

    def __zeroOrElse(self):
        if len(self.__line) != 0:
            print("ERROR...")
            print(self.__line)
            print("Remaining elements...")
            sys.exit(1)

    def _debit(self, line: list):
        """
        Debit type transaction
        """
        self.__line.pop()
        self.__setDate()
        self.__setDescription()
        self.__setDebitAmount()
        self.__popAZeroOrElse()
        self.__popValueInTitleOrElse("確定", "利用", "取消")
        self.__popCount(3)
        self.__setDebitID()
        self.__line.pop()
        self.__line.pop()
        self.__zeroOrElse()

    def _bank(self, line: list):
        """
        Bank type transaction without debit entry
        """
        self.__setDate()
        self.__popCount(4)
        self.__setReplaceDescription()
        self.__setAmount()
        self.__setBalance()
        self.__emptyOrElse()
        self.__zeroOrElse()

    def bankOverDebit(self, line: list):
        """
        Bank type transaction
        """
        line.reverse()
        self.__line = line
        self.__setDate()
        self.__popCount(5)
        self.__setAmount()
        self.__setBalance()
        self.__emptyOrElse()
        self.__zeroOrElse()

class Transactions():
    """
    Global transactions
    """
    def __init__(self, startYear: str, startMonth: str, startDay: str, files: list):
        self.__startYear = int(startYear)
        self.__startMonth = int(startMonth)
        self.__startDay = int(startDay)
        self.__transactions = list()
        self.__files = dict()
        self.__debitIDs = dict()
        for file in files:
            with codecs.open(file, encoding="shift_jis") as fd:
                line = fd.readline().rstrip("\n").rstrip("\r")
                if line == '"操作日(年)","操作日(月)","操作日(日)","操作時刻(時)","操作時刻(分)","操作時刻(秒)","取引順番号","摘要","お支払金額","お預り金額","残高","メモ"':
                    self.__files["_bank"] = file
                elif line == '"カード番号","利用年","利用月","利用日","利用店名","利用金額（円）","未払金（円）","取引状況","外貨コード","外貨金額","外貨レート","取引明細番号","支払方法","支払オプション"':
                    self.__files["_debit"] = file
                else:
                    print("Unknown file: %s" % file)
                    sys.exit(1)
        self.__mode = "_debit"
        for line in csv.reader(codecs.open(self.__files[self.__mode], encoding="shift_jis")):
            if line[0] == "カード番号":
                continue
            transaction = Transaction(self, line)
            if datetime.datetime.strptime(transaction.getDate(), '%Y/%m/%d') < datetime.datetime(self.__startYear, self.__startMonth, self.__startDay):
                continue
            self.__transactions.append(transaction)
        self.__mode = "_bank"
        for self.__line in csv.reader(codecs.open(self.__files[self.__mode], encoding="shift_jis")):
            if self.__line[0] == "操作日(年)":
                continue
            if self.__bankDescription().startswith("Vデビット"):
                self.__getDebit().bankOverDebit(self.__line)
                continue
            transaction = Transaction(self, self.__line)
            if datetime.datetime.strptime(transaction.getDate(), '%Y/%m/%d') > datetime.datetime(self.__startYear, self.__startMonth, self.__startDay):
                self.__transactions.append(transaction)

        transaction: Transaction
        transaction = self.__transactions[0]
        runningBalance = transaction.getBalance()
        transaction.setHash()
        for transaction in self.__transactions[1:]:
            runningBalance += transaction.getAmount()
            transaction.setBalance(runningBalance)
            transaction.setHash()
        if runningBalance != self.__lastBalance:
            print("Balances do not match %d != %d!" % (runningBalance, self.__lastBalance))
            sys.exit(1)

        rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        rowWriter.writerow(("Txn ID", "Date", "Name", "Amount", "Balance"))
        for transaction in self.__transactions:
            rowWriter.writerow([
                transaction.getHash(),
                transaction.getDate(),
                transaction.getDescription(),
                transaction.getAmount(),
                transaction.getBalance(),
            ])

    def mode(self) -> str:
        return self.__mode

    def __bankDescription(self) -> str:
        return self.__line[-5]

    def __getDebit(self) -> Transaction:
        return self.__debitIDs[self.__bankDescription().split("\u3000")[-1]]

    def setDebit(self, transaction: Transaction):
        self.__debitIDs[transaction.getDebitID()] = transaction

    def setLastBalance(self, transaction: Transaction):
        self.__lastBalance = transaction.getBalance()

def jnbBank(startYear: str, startMonth: str, startDay: str, files: list):
    Transactions(startYear, startMonth, startDay, files)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("%s <year> <month> <day> <meisai> <meisai>" % sys.argv[0])
        sys.exit(1)
    jnbBank(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:6])

# XXX probably need to rewrite to this to use just the bank account .csv file and ignore the debit.csv
# XXX so don't need to download the debit csv file.

# XXX need to figure out why these transaction hashes keep changing.
# XXX best to keep a CSV file around and see that they are changing.
    # XXX see the 'safe' directory.
