#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import glob
import os
import sys
import codecs
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime

def neobankAll(dirname: str):
    from forge import bankRun

    def bankRunGenerator(outputFile: str) -> list[bankRun]:

        def download():
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

def neobankBank(filename: str):
    DATE = "お取引日"
    EXPENSE = "お取引金額"
    DESCRIPTION = "お取引内容"

    @dataclass
    class transaction:
        epoch: str
        date: str
        amount: int
        name: str

    columns = {}
    epochIncrements = defaultdict(int)

    def handleRemainingLines(line: list):
        def getElement(column: str) -> str:
            return line[columns[column]]

        def getEpoch() -> str:
            nonlocal columns
            nonlocal epochIncrements
            epoch = int(datetime.strptime(getElement(DATE), '%Y/%m/%d').strftime("%s"))
            epochIncrements[epoch]+=1
            return str(epoch * 100 + (100-epochIncrements[epoch]))

        nonlocal columns
        return transaction(
            epoch=getEpoch(),
            date=getElement(DATE),
            # lazily avoiding dealing with potential prefixed +
            amount=int("-"+getElement(EXPENSE).replace(".00","")),
            name=getElement(DESCRIPTION),
        )

    def handleFirstLine(line: list):
        nonlocal handler
        nonlocal columns
        columns = dict(map(lambda numberValue: (numberValue[1],numberValue[0]), enumerate(line)))
        handler = handleRemainingLines
        return None

    handler = handleFirstLine
    def handle(line: list):
        return handler(line)

    def getTransactions() -> list[transaction]:
        return list(reversed([ item for item in
                    map( handle, csv.reader(codecs.open(filename, "r", "shift_jis")))
                if item is not None ]))

    rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
    rowWriter.writerow(("Txn ID", "Date", "Name", "Amount"))
    for row in getTransactions():
        rowWriter.writerow((
            row.epoch,
            row.date,
            row.name,
            row.amount,
        ))

if __name__ == '__main__':
    FILE = 1
    neobankBank(sys.argv[FILE])
