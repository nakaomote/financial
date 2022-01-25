#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Rakuten's CSV files
"""

import codecs
import csv
import sys
import datetime
import hashlib

if len(sys.argv) != 3:
    print("%s <meisai> <meisai>" % sys.argv[0])
    sys.exit(1)

MISSINGDEBIT = 0
FILES = dict()
for file in sys.argv[1:3]:
    with codecs.open(file, "r") as fd:
        line = fd.readline().rstrip("\n").rstrip("\r")
        if line == "取引日,入出金(円),取引後残高(円),入出金内容":
            FILES["kouzaFile"] = file
        elif line == '"ご利用日","ご利用先","ご利用金額（円）","現地通貨額","通貨略称","換算レート","使用地域","照会番号","承認番号","口座引落分（円）","ポイント利用分"':
            FILES["debitFile"] = file
        else:
            print("Unknown file: %s" % file)
            sys.exit(1)

class Skip:
    pass

def returnValue(value):
    return value

def dateFix(date: str, line: list):
    return returnValue, datetime.datetime.strptime(date, '%Y%m%d').strftime("%Y/%m/%d")

def addMinus(amount: str, line: list):
    return returnValue, -int(amount)

def getValue(value: str, line: list):
    return returnValue, value

def alwaysZero(value: str, line: list):
    if value != "0":
        print("Points not zero which we never encountered before...")
        sys.exit(1)
    return returnValue, None

def matchAmount(value: str, line: list):
    if line[2] != line[9]:
        print("Price doesn't match other price which we never encountered before...")
        sys.exit(1)
    return returnValue, None

HANDLER = {
  0: False,
  1: getValue,
  2: addMinus,
  3: False,
  4: False,
  5: False,
  6: False,
  7: False,
  8: False,
  9: matchAmount,
  10: alwaysZero,
}

csv.reader(codecs.open(FILES["debitFile"], "r"))
debitEntries = dict()
for line in csv.reader(codecs.open(FILES["debitFile"], "r")):
    if line[0] == "ご利用日":
        continue
    newLine = list()
    for index, item in enumerate(line):
        if HANDLER[index] is False:
            continue
        action, value = HANDLER[index](item, line)
        newValue = action(value)
        if newValue is not None:
            newLine.append(newValue)
    debitEntries["A0" + line[8]] = newLine

def getDebit(value: str, line: list):
    debitKey = None
    if value.startswith("VISAデビット"):
        debitKey = value.split(" ")[1]
        if debitKey not in debitEntries:
            print("Debit entry not found for: %s" % debitKey, file=sys.stderr)
            return returnValue, Skip
        if debitEntries[debitKey][1] != int(line[1]):
            print("Debit amount doesn't match account amount: %s" % debitKey)
            sys.exit(1)
    if debitKey is not None:
        value = debitEntries[debitKey][0]
    return returnValue, value

HANDLER = {
  0: dateFix,
  1: getValue,
  2: getValue, # Much easier with this.
  3: getDebit,
}
rows = dict()
for line in csv.reader(codecs.open(FILES["kouzaFile"], "r")):
    if line[0] == "取引日":
        continue
    newLine = list()
    for index, item in enumerate(line):
        if HANDLER[index] is False:
            continue
        action, value = HANDLER[index](item, line)
        newValue = action(value)
        if newValue is not None:
            newLine.append(newValue)

    if len(newLine) != 4:
        print("Line without 4 entries!")
        print(newLine)
        sys.exit(1)
    day     = newLine[0]
    amount  = newLine[1]
    balance = newLine[2]
    name    = newLine[3]

    if Skip in newLine:
        MISSINGDEBIT += int(amount)
        continue

    m = hashlib.md5()
    m.update(
        day.encode("utf-8") +
        name.encode("utf-8") +
        balance.encode("utf-8") +
        amount.encode("utf-8")
    )
    hash = m.hexdigest()
    if not hash in rows:
        rows[hash] = list()
    rows[hash].append([ day, name, int(amount), int(balance) ])

rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
for row, entries in rows.items():
    for index, values in enumerate(entries):
        rowWriter.writerow([ row + "_" + str(index) ] + values)

print("Missing debit amount: %d" % MISSINGDEBIT, file=sys.stderr)
