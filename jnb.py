#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Japan Net Bank CSV files
"""

import codecs
import csv
import sys
import datetime
import hashlib

if len(sys.argv) != 4:
    print("%s <meisai> <meisai>" % sys.argv[0])
    sys.exit(1)

FILES = dict()
runningBalance = None
for file in sys.argv[2:4]:
    with codecs.open(file, "r", 'shift_jis') as fd:
        line = fd.readline().rstrip("\n").rstrip("\r")
        if line == '"操作日(年)","操作日(月)","操作日(日)","操作時刻(時)","操作時刻(分)","操作時刻(秒)","取引順番号","摘要","お支払金額","お預り金額","残高","メモ"':
            FILES["kouzaFile"] = file
        elif line == '"カード番号","利用年","利用月","利用日","利用店名","利用金額（円）","未払金（円）","取引状況","外貨コード","外貨金額","外貨レート","取引明細番号","支払方法"':
            FILES["debitFile"] = file
        else:
            print("Unknown file: %s" % file)
            sys.exit(1)

def returnValue(value):
    return value

def dateFix(date: str, line: list):
    return returnValue, datetime.datetime.strptime(
                "%d%02d%02d" % (int(line[0]), int(line[1]), int(line[2])), '%Y%m%d'
            ).strftime("%Y/%m/%d")

def addMinus(amount: str, line: list):
    return returnValue, int("-" + amount)

def getValue(value: str, line: list):
    return returnValue, value

def getInt(value: str, line: list):
    return returnValue, int(value)

def alwaysZero(value: str, line: list):
    if value != "0":
        print("Points not zero which we never encountered before...")
        sys.exit(1)
    return returnValue, None

def alwaysEmpty(value: str, line: list):
    if len(value) != 0:
        print("Field is not empty...")
        sys.exit(1)
    return returnValue, None

def isDebit(value: str, line: list):
    if value != "Visaデビット":
        print("Isn't set to Visaデビット")
        sys.exit(1)
    return returnValue, None

DEBIT_HANDLER = {
  0: False,
  1: False,
  2: False,
  3: False,
  4: getValue,
  5: addMinus,
  6: alwaysZero,
  7: False,
  8: False,
  9: False,
  10: False,
  11: False,
  12: isDebit,
}

csv.reader(codecs.open(FILES["debitFile"], "r", "shift_jis"))
debitEntries = dict()
debitHolds   = dict()
for line in csv.reader(codecs.open(FILES["debitFile"], "r", "shift_jis")):
    if line[0] == "カード番号":
        continue
    newLine = list()
    for index, item in enumerate(line):
        if DEBIT_HANDLER[index] is False:
            continue
        action, value = DEBIT_HANDLER[index](item, line)
        newValue = action(value)
        if newValue is not None:
            newLine.append(newValue)
    debitEntries[line[11]] = newLine

def getDebitKey(value: str) -> str:
    return value.split("(")[1].split(")")[0]

def getDebit(value: str, line: list):
    if value.startswith("Visaデビット売上確定("):
        debitKey = getDebitKey(value)
        if len(line[8]) != 0 and len(line[9]) != 0:
            print("Both amounts cannot have values!")
            sys.exit(1)
        debitHeld = 0
        if debitKey in debitHolds:
            debitHeld = debitHolds[debitKey]
        if len(line[8]) != 0:
            if debitEntries[debitKey][1] == (0 - debitHeld - int(line[8])):
                return returnValue, debitEntries[debitKey][0]
        if len(line[9]) != 0:
            if debitEntries[debitKey][1] == (0 - debitHeld + int(line[9])):
                return returnValue, debitEntries[debitKey][0]
        print("Debit amounts did not add up!")
        sys.exit(1)
    if value.startswith("Visaデビット売上予約("):
        debitKey = getDebitKey(value)
        if debitKey not in debitEntries:
            print(line)
            print("Debit entry not found for: %s" % debitKey)
            sys.exit(1)
        if len(line[8]) == 0:
            print("Visaデビット売上予約 should never be empty!")
            sys.exit(1)
        if debitEntries[debitKey][1] != int("-" + line[8]):
            debitHolds[debitKey] = int(line[8])
            return debitHold, None
        return returnValue, debitEntries[debitKey][0]
    return returnValue, value

def debitHold(value):
    print("This method should never run!")
    sys.exit(1)
    pass

def getAmount(value: str, line: list):
    if line[7].startswith("Visaデビット売上確定("):
        debitKey = getDebitKey(line[7])
        if debitKey in debitHolds:
            del debitHolds[debitKey]
        return returnValue, debitEntries[debitKey][1]

    if len(value) != 0 and len(line[9]) != 0:
        print("Both amounts cannot have values!")
        sys.exit(1)

    if len(value) != 0:
        return returnValue, int("-" + value)

    if len(line[9]) != 0:
        return returnValue, int(line[9])

def checkBalance(runningBalance: int, amount: int, balance: int) -> int:
    if runningBalance is None:
        return balance
    if balance != runningBalance + amount:
        print("Something does not add up!")
        sys.exit(1)
    runningBalance = runningBalance + amount

def handleLine(line: list):
    newLine = list()
    for index, item in enumerate(line):
        if KOUZA_HANDLER[index] is False:
            continue
        action, value = KOUZA_HANDLER[index](item, line)
        if action is debitHold:
            return None
        newValue = action(value)
        if newValue is not None:
            newLine.append(newValue)
    if len(newLine) != 5:
        print("Line without 5 entries!")
        print(newLine)
        sys.exit(1)
    return newLine

KOUZA_HANDLER = {
  0: dateFix,
  1: False,
  2: False,
  3: False,
  4: False,
  5: False,
  6: getValue,
  7: getDebit,
  8: getAmount,
  9: False,
  10: getInt, # Balance, easier to see.
  11: alwaysEmpty,
}

rows = dict()
startingBalance = int(sys.argv[1])
for line in csv.reader(codecs.open(FILES["kouzaFile"], "r", "shift_jis")):
    if line[0] == "操作日(年)":
        continue
    newLine = handleLine(line)
    if newLine is None:
        continue

    day      = newLine[0]
    sequence = newLine[1]
    name     = newLine[2]
    amount   = newLine[3]
    balance  = newLine[4]

    runningBalance = checkBalance(runningBalance, amount, balance)

    if startingBalance is not None:
        if balance != startingBalance:
            continue
        elif balance == startingBalance:
            startingBalance = None
            continue

    m = hashlib.md5()
    m.update(
        day.encode("utf-8") +
        sequence.encode("utf-8") +
        name.encode("utf-8") +
        str(balance).encode("utf-8") +
        str(amount).encode("utf-8")
    )
    hash = m.hexdigest()
    if not hash in rows:
        rows[hash] = list()
    rows[hash].append([ day, sequence, name, int(amount), int(balance) ])

if len(debitHolds) != 0:
    print("debitHolds is not empty...")
    sys.exit(1)

rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
for row, entries in rows.items():
    for index, values in enumerate(entries):
        rowWriter.writerow([ row + "_" + str(index) ] + values)
