#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import glob
import os
import sys
import codecs
from datetime import datetime
from typing import Union
from descriptions import Descriptions
from funktions import standardBankRowHandlerGeneration, writeUploadableTransactionsCSV

def neobankAll(dirname: str):
    from forge import bankRun

    def bankRunGenerator(outputFile: str) -> list[bankRun]:

        def download():
            while input("Download neobank csv file and type 'yes': ") != "yes":
                pass

        def parse():
            file = glob.glob(
                os.path.join(
                    os.environ["HOME"],
                    "ダウンロード",
                    "meisai*.csv"
                )
            )[0]
            neobankBank(file)
            os.remove(file)


        return [bankRun(
            filename=os.path.join(dirname, outputFile),
            download=download,
            parse=parse,
        )]

    return bankRunGenerator(os.path.join(dirname,"neobank.csv"))

def neobankBank(meisai: str):

    def getDateTimeBase(mapOfValues) -> datetime:
        return datetime.strptime(mapOfValues["お取引日"], "%Y/%m/%d")

    def getDescription(mapOfValues):
        baseDescription = mapOfValues["お取引内容"]
        return Descriptions().getName(baseDescription)

    def getAmount(mapOfValues) -> int:
        amount = mapOfValues["お取引金額"]
        return 0 - int(float(amount))

    def getBalance(mapOfValues) -> Union[int, None]:
        return None

    def readCsvFile():
        return csv.reader(codecs.open(meisai, "r", "shift_jis"))

    def skipBeforeStartDateCheck(dateTimeBase: datetime) -> bool:
        return False

    writeUploadableTransactionsCSV(
        fileReader = readCsvFile,
        mapFunction = standardBankRowHandlerGeneration(
            getDateTimeBase = getDateTimeBase,
            getSkipBeforeStartDateCheck = skipBeforeStartDateCheck,
            getDescription = getDescription,
            getAmount = getAmount,
            getBalance = getBalance,
        ),
        needReverse = True,
    )


if __name__ == '__main__':
    FILE = 1
    neobankBank(sys.argv[FILE])

# TODO: Fix bug in this that has international items not billed correctly due to a fee.
# The value comes in from the column "海外事務手数料"
