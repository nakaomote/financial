#!/usr/bin/env python3

from functools import reduce
from typing import Any, Callable, Union
from dataclasses import dataclass

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
class LinkedRow:
    index: int
    last: Union['LinkedRow',None]
    this: Callable

def getLazyValue(function: Callable):
    response = None # I'm sorry mutations.
    set = None
    def run(handler: Callable = lambda x: x):
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

def getLazyDictLinkedListWithHandler(fileReader: Callable) -> list[LinkedRow]:
    listOfDictFunctions = list(map(lambda function: getLazyValue(function), getDictOfLazyRowsWithHeader(fileReader)))
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


def mapCsvRowsIgnoreNone(fileReader: Callable, mapFunction: Callable):
    def ignoreNone(acc: list, value: LinkedRow):
        response = mapFunction(value)
        return acc if response is None else acc + [response]
    return list(
        reduce(
            ignoreNone,
            getLazyDictLinkedListWithHandler(
                fileReader=fileReader,
            ),
            [],
        )
    )
