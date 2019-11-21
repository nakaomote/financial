#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import codecs
import csv
import io
import hashlib
import pprint

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='shift-jis')
rows = dict()
for line in csv.reader(sys.stdin, delimiter=',', quotechar='"'):
    if line[3] != "JCB加盟店":
        if line[0] == "行":
            continue
        day    = line[2][0:10]
        name   = line[3]
        amount = line[4].replace(",","") if line[1] == "チャージ" else "-" + line[4].replace(",","")
        m = hashlib.md5()
        m.update(day.encode("utf-8") + name.encode("utf-8") + amount.encode("utf-8"))
        hash = m.hexdigest()
        if not hash in rows:
            rows[hash] = list()
        rows[hash].append([ day, name, int(amount)])

rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
for row, entries in rows.items():
    for index, values in enumerate(entries):
        rowWriter.writerow([ row + "_" + str(index) ] + values)
