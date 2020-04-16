#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Seven 11's CSV file
"""

import sys
import io
import csv

"""
Handle credits
"""
def credit(row: list) -> list:
    row.pop(5)
    row[3] = row[3].replace("-","")
    row[5] = "+" + row[5]
    return row

"""
Handle debits
"""
def debit(row: list) -> list:
    row[3] = "-" + row[3].replace(",","")
    return row

rowSizes = {
    credit: 7,
    debit: 6,
}

"""
Filter out noise
"""
def bouncer(row: list, handler) -> None:
    if mode is None:
        return None
    if rowSizes[handler] != len(row):
        raise Exception("Row items have an incorrect count!")
    if row[0] == "ご利用者":
        return None
    rowWriter.writerow(handler(row))

categoryHeaders = {
    "◆ご利用明細内訳（お振替済分）": debit,
    "◆ご利用明細内訳（差額分・お振替未済分）": credit,
}

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='shift-jis')
rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
mode = None
for line in csv.reader(sys.stdin, delimiter=',', quotechar='"'):
    if len(line) == 0:
        continue
    if line[0] in categoryHeaders:
        mode = categoryHeaders[line[0]]
        continue
    bouncer(line, mode)
