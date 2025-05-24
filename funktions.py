#!/usr/bin/env python3

from functools import reduce
from typing import Any, Callable, Union
from dataclasses import dataclass
import datetime

def getLazyRows(fileReader: Callable) -> list[Callable]:
    return list(map(lambda csvRow: lambda handler: handler(enumerate(csvRow)), fileReader()))

def getColumnsIndexMap(lazyCsvRow: Callable):
    return dict(map(lambda numberValue: (numberValue[0],numberValue[1]), lazyCsvRow(lambda csvRow: csvRow)))

def getDictOfLazyRowsFromLazyRowList(lazyRows: list, columns: dict) -> list[Callable]:
    return list(
        map(
            lambda lazyCsvRow: lambda handler: handler(
                dict(
                    map(
                        lambda numberValue: (columns[numberValue[0]],numberValue[1]),
                        lazyCsvRow(lambda csvRow: csvRow)
                    )
                )
            ), lazyRows
        )
    )

@dataclass
class StandardBankTransaction:
    description: str
    dateString: str
    datetime: datetime.datetime
    amount: int
    balance: int
    sameDayCount: int

    def createTransactionId(self):
        return self.dateString.replace("/","") + "%04d" % self.sameDayCount

@dataclass
class LinkedRow:
    index: int
    last: Union['LinkedRow',None]
    this: Callable

def getLazyValue(function: Callable, defaultHandler: Callable = lambda x: x):
    response = None # I'm sorry mutations.
    set = None
    def run(handler: Callable = defaultHandler):
        nonlocal response
        nonlocal set
        if set is None:
            response = function(handler)
            set = True
        return response
    return run

def reduceLinkedRow(indexAndFunction: tuple, last: Union[LinkedRow,None]) -> LinkedRow:
    index = indexAndFunction[0]
    function = indexAndFunction[1]
    return LinkedRow(
        index=index,
        last=last,
        this=function,
    )

def getLazyDictLinkedListWithHandler(fileReader: Callable, defaultHandler: Callable = lambda x: x) -> list[LinkedRow]:
    listOfDictFunctions = list(map(lambda function: getLazyValue(function, defaultHandler), getDictOfLazyRowsWithHeader(fileReader)))
    return list(
        reduce(
            lambda acc, indexAndFunction: acc + [reduceLinkedRow(indexAndFunction, acc[-1] if len(acc) > 0 else None)],
            enumerate(listOfDictFunctions),
            []
        )
    )

def getDictOfLazyRowsWithHeader(fileReader: Callable) -> list[Callable]:
    lazyRows = getLazyRows(fileReader)
    columns = getColumnsIndexMap(lazyRows[0])
    return getDictOfLazyRowsFromLazyRowList(lazyRows[1:], columns)


def mapCsvRowsIgnoreNone(fileReader: Callable, mapFunction: Callable, defaultHandler: Callable = lambda x: x):
    def ignoreNone(acc: list, value: LinkedRow):
        response = mapFunction(value)
        return acc if response is None else acc + [response]
    return list(
        reduce(
            ignoreNone,
            getLazyDictLinkedListWithHandler(
                fileReader=fileReader,
                defaultHandler=defaultHandler,
            ),
            [],
        )
    )


def standardBankRowHandlerGeneration(
    getDateTimeBase: Callable,
    getSkipBeforeStartDateCheck: Callable,
    getDescription: Callable,
    getAmount: Callable,
    getBalance: Callable,
) -> Callable:
    def standardBankRowHandler(value: LinkedRow):
        last: Union[LinkedRow,None] = value.last
        def mapToDataClass(mapOfValues: dict):
            dateTimeBase = getDateTimeBase(mapOfValues)
            if getSkipBeforeStartDateCheck(dateTimeBase):
                return None
            dateTimeString = dateTimeBase.strftime('%Y/%m/%d')
            sameDayCount = last.this().sameDayCount + 1 \
                if last and last.this() and last.this().dateString == dateTimeString \
                else 0
            return StandardBankTransaction(
                description = getDescription(mapOfValues),
                dateString = dateTimeString,
                datetime = dateTimeBase,
                amount = getAmount(mapOfValues),
                balance = getBalance(mapOfValues),
                sameDayCount = sameDayCount
            )

        transaction: StandardBankTransaction = value.this(mapToDataClass)
        if last is not None and last.this() and transaction is not None:
            lastTransaction: StandardBankTransaction = last.this()
            if lastTransaction.balance + transaction.amount != transaction.balance:
                print(transaction.amount)
                raise Exception(
                        f"""
                            Balance not matching ->
                            lastTransaction.balance: {lastTransaction.balance}
                            transaction.balance: {transaction.balance}
                            transaction.amount: {transaction.amount}
                            {lastTransaction.balance} != {transaction.balance}
                        """
                )

        return transaction
    return standardBankRowHandler
