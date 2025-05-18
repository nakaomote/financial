#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sony Bank
"""

import csv
import sys
import codecs
from datetime import datetime
import hashlib
from descriptions import Descriptions
import configparser
import os
from funktions import StandardBankTransaction, mapCsvRowsIgnoreNone, standardBankRowHandlerGeneration
from sony_download import sonyDownload

def sonyAll(dirname: str):
    from forge import bankRun

    downloadFile = "YenFutsuRireki.csv"

    def bankRunGenerator(sonySection: str) -> bankRun:
        finalFile = f"sony-{sonySection}.csv"

        def download():
            sonyDownload(sonySection)

        def parse():
            sonyBank(downloadFile, "2025-03-23")
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
    dateTimeStartDate = datetime.strptime(startDate, '%Y-%m-%d')

    def getDateTimeBase(mapOfValues) -> datetime:
        return datetime.strptime(mapOfValues["取引日"], "%Y年%m月%d日")

    def getDescription(mapOfValues):
        baseDescription = mapOfValues["摘要"]
        return Descriptions().getName(
            baseDescription.split("　")[-1]
            if baseDescription.startswith("Visaデビット")
            else baseDescription
        )

    def getAmount(mapOfValues) -> int:
        return 0 - int(float(mapOfValues["引出額"] or 0)) + int(float(mapOfValues["預入額"] or 0))

    def getBalance(mapOfValues) -> int:
        return int(float(mapOfValues["差引残高"]))

    def readCsvFile():
        return csv.reader(codecs.open(meisai, "r", "shift_jis"))

    def skipBeforeStartDateCheck(dateTimeBase: datetime) -> bool:
        return dateTimeBase < dateTimeStartDate

    listofTransactions: list[StandardBankTransaction] = \
        mapCsvRowsIgnoreNone(
            fileReader = readCsvFile,
            mapFunction = standardBankRowHandlerGeneration(
                getDateTimeBase = getDateTimeBase,
                getSkipBeforeStartDateCheck = skipBeforeStartDateCheck,
                getDescription = getDescription,
                getAmount = getAmount,
                getBalance = getBalance,
            )
        )

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
    if len(sys.argv) != 3:
        print("%s <meisai> <start-date>" % sys.argv[0])
        sys.exit(1)

    sonyBank(sys.argv[1], sys.argv[2])
