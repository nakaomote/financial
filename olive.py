#!/usr/bin/env python3

import csv
import sys
import codecs
import os
import glob
from datetime import datetime
from dataclasses import dataclass

def oliveAll(dirname: str):
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
            oliveBank(file)
            os.remove(file)

        return [bankRun(
            filename=os.path.join(dirname, outputFile),
            download=download,
            parse=parse,
        )]

    return bankRunGenerator(os.path.join(dirname,"olive.csv"))


def oliveBank(file: str):
    DATE = 0
    NAME = 3
    INCOME = 2
    OUTGOING = 1
    BALANCE = 4

    transactionsOrder = list()
    transactionsDates = dict()

    @dataclass
    class transaction:
        epoch: int
        date: str
        amount: int
        name: str
        balance: int

    def handleLine(line: list) -> transaction:
        return transaction(
            int(datetime.strptime(line[DATE], '%Y/%m/%d').strftime("%s")) * 100,
            datetime.strptime(line[DATE], '%Y/%m/%d').strftime("%m/%d/%Y"),
            0 - int(line[OUTGOING]) if line[INCOME] == "" else int(line[INCOME]),
            line[NAME],
            line[BALANCE],
        )

    for line in csv.reader(codecs.open(file, "r", "shift_jis")):
        date = line[DATE]

        if date == "年月日":
            continue

        if date in transactionsDates:
            transactionsDates[date].append(handleLine(line))
            continue

        transactionsDates[date] = [handleLine(line)]
        transactionsOrder.append(transactionsDates[date])

    rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
    rowWriter.writerow(("Txn ID", "Date", "Name", "Amount", "Balance"))
    for transactionDate in reversed(transactionsOrder):
        for index, transaction in enumerate(reversed(transactionDate)):
            rowWriter.writerow((
                transaction.epoch + index + 1,
                transaction.date,
                transaction.name,
                transaction.amount,
                transaction.balance,
            ))

if __name__ == '__main__':
    FILE = 1
    oliveBank(sys.argv[FILE])
