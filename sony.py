#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sony Bank
"""

import csv
import glob
import sys
import codecs
from datetime import datetime
from typing import Union
from descriptions import Descriptions
import configparser
import os
from funktions import LinkedRow, StandardBankTransaction, getStandardCsvHeaders, mapCsvRowsIgnoreNone, readCsvFileFunction, standardBankRowHandlerGeneration, writeUploadableTransactionsCSV

def sonyAll(dirname: str):
    from forge import bankRun

    def bankRunGenerator(sonySection: str) -> bankRun:
        finalFile = f"sony-{sonySection}.csv"

        def download():
            while input(f"Download sony csv file for '{sonySection}' and type 'yes': ") != "yes":
                pass

        def getFinalBalance() -> dict[str,int]:
            return {}

        def parse():
            file = glob.glob(
                os.path.join(
                    os.environ["HOME"],
                    "ダウンロード",
                    "FutsuRireki.csv"
                )
            )[0]
            sonyBank(file, "2025-05-23")
            os.remove(file)

        def createSplits() -> None:
            def handleFilter(value: LinkedRow):
                this = value.this()
                name = this["Name"]
                if name in ("モバイルＰＡＳＭＯチャージ", "ＰＡＳＭＯ"):
                    return this
                return None

            listofTransactions = \
                mapCsvRowsIgnoreNone(
                    readCsvFileFunction(os.path.join(dirname, finalFile), "utf-8"),
                    handleFilter
                )

            if len(listofTransactions) == 0:
                return

            with open(os.path.join(dirname, finalFile.replace(".csv","-pasumo.csv")), "w") as rb:
                rowWriter = csv.writer(rb, delimiter=',', quotechar='"')
                headers = getStandardCsvHeaders()
                rowWriter.writerow(headers)
                for transaction in listofTransactions:
                    rowWriter.writerow(tuple(map(lambda x: transaction[x], headers)))

        return bankRun(
            filename=os.path.join(dirname, finalFile),
            download=download,
            parse=parse,
            finalBalance=getFinalBalance,
            createSplits=createSplits,
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

    writeUploadableTransactionsCSV(
        fileReader = readCsvFile,
        mapFunction = standardBankRowHandlerGeneration(
            getDateTimeBase = getDateTimeBase,
            getSkipBeforeStartDateCheck = skipBeforeStartDateCheck,
            getDescription = getDescription,
            getAmount = getAmount,
            getBalance = getBalance,
        )
    )

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("%s <meisai> <start-date>" % sys.argv[0])
        sys.exit(1)

    sonyBank(sys.argv[1], sys.argv[2])
