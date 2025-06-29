#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PayPay Bank
"""

import csv
import codecs
import sys
import datetime
import os
import glob
from typing import Callable, Union
from descriptions import Descriptions
from funktions import LinkedRow, setLastBalance, mapCsvRowsIgnoreNone, readCsvFileFunction
from jnb_download import jnbDownload
from dataclasses import dataclass

def jnbAll(dirname: str):
    from forge import bankRun

    def bankRunGenerator(outputFile: str) -> list[bankRun]:
        year = None
        month = None
        day = None
        finalBalance = None
        fullPathOutputFile = os.path.join(dirname, outputFile)

        def configureAndDownload():
            nonlocal year
            nonlocal month
            nonlocal day
            year = input("Start year (jnb): ")
            month = input("Start month (jnb): ")
            day = input("Start day (jnb): ")
            jnbDownload()

        def setFinalBalance(value: int) -> None:
            nonlocal finalBalance
            finalBalance = value

        def getFinalBalance() -> Union[None, int]:
            nonlocal finalBalance
            if finalBalance is None:
                 setLastBalance(
                     fileReader = readCsvFileFunction(fullPathOutputFile, "utf-8"),
                     setFinalBalance = setFinalBalance,
                 )
            return finalBalance

        def parse():
            nonlocal year
            nonlocal month
            nonlocal day
            files = glob.glob(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "NBG*"
                )
            )
            jnbBank(str(year),str(month),str(day),files[0])
            for file in files:
                os.remove(file)

        return [bankRun(
            filename=fullPathOutputFile,
            download=configureAndDownload,
            parse=parse,
            finalBalance=getFinalBalance,
        )]

    return bankRunGenerator(os.path.join(dirname,"jnb.csv"))

@dataclass
class JnbTransaction:
    description: str
    dateString: str
    datetime: datetime.datetime
    amount: int
    balance: int
    sameDayCount: int

    def createTransactionId(self):
        return self.dateString.replace("/","") + "%04d" % self.sameDayCount

def jnbBank(startYear: str, startMonth: str, startDay: str, file: str):
    def readCsvFile():
        return csv.reader(codecs.open(file, "r", "shift_jis"))

    def handleJnbBankRow(value: LinkedRow):
        last: Union[LinkedRow,None] = value.last

        def mapToDataClass(mapOfValues: dict):
            nonlocal last
            dateTimeBase = datetime.datetime.strptime(
                                "/".join(
                                    map(lambda x: mapOfValues[x], ("操作日(年)", "操作日(月)", "操作日(日)"))
                                    ),
                                '%Y/%m/%d'
                            )
            if dateTimeBase < datetime.datetime(int(startYear), int(startMonth), int(startDay)):
                return None
            dateTimeString = dateTimeBase.strftime('%Y/%m/%d')
            sameDayCount = last.this().sameDayCount + 1 if last and last.this() and last.this().dateString == dateTimeString else 0
            debitRemoveDescription = Descriptions().getName(mapOfValues["摘要"].replace("Vデビット　", ""))
            description = debitRemoveDescription[0:debitRemoveDescription.index("　2A")] if "　2A" in debitRemoveDescription else debitRemoveDescription
            return JnbTransaction(
                description=description,
                dateString=dateTimeString,
                datetime=dateTimeBase,
                amount=0 - int(mapOfValues["お支払金額"] or 0) + int(mapOfValues["お預り金額"] or 0),
                balance=int(mapOfValues["残高"]),
                sameDayCount=sameDayCount,
            )

        transaction: JnbTransaction = value.this(mapToDataClass)
        if last is not None and last.this() and transaction is not None:
            lastTransaction: JnbTransaction = last.this()
            if lastTransaction.balance + transaction.amount != transaction.balance:
                raise Exception("Balance not matching!")

        return transaction

    listofTransactions: list[JnbTransaction] = mapCsvRowsIgnoreNone(readCsvFile, handleJnbBankRow)
    rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
    rowWriter.writerow(("Txn ID", "Date", "Name", "Amount", "Balance"))
    for transaction in listofTransactions:
        rowWriter.writerow((
            transaction.createTransactionId(),
            transaction.dateString,
            transaction.description,
            transaction.amount,
            transaction.balance,
        ))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("%s <year> <month> <day> <meisai> <meisai>" % sys.argv[0])
        sys.exit(1)
    jnbBank(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
