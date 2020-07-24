#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Reading in pasumo data from Suica リーダー + 家計簿 = スイ家計簿's CSV file
"""

import csv
import sys

if len(sys.argv) != 2:
    print("%s <meisai>" % sys.argv[0])
    sys.exit(1)

class Transactions:
    class HeaderTracker:
        def __init__(self, line: list):
            self.headers = dict()
            for index, item in enumerate(line):
                self.headers[index] = item

        # This is for debugging and may not remain in use.
        def print_line(self, line: list):
            for index in range(0, len(line)):
                print("%d:	%s	%s:		%s" % (index, type(line[index]), self.headers[index], line[index]))

    class Transaction:

        class TransactionsDetails:
            def __init__(self, line: list, lastTransaction):
                self.line = line
                self.__amount = None
                if self.getAmount() == 0:
                    if lastTransaction is None:
                        self.__amount = self.getBalance()
                    else:
                        self.__amount = self.getBalance() - lastTransaction.getBalance()

            def getRow(self) -> list:
                return [ self.getSerialNumber(), self.getDate(), self.getName(), self.getAmount(), self.getBalance() ]

            def getSerialNumber(self) -> int:
                return int(self.line[0])

            def getDate(self) -> str:
                return self.line[1]

            def getAmount(self) -> int:
                if self.__amount is not None:
                    return self.__amount
                return -int(self.line[2])

            def getBalance(self) -> int:
                return int(self.line[4])

            def getName(self) -> None:
                raise Exception("%s getName should never run!" % self)

        class Transport(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> int:
                return ("%s (%s/%s) -> %s (%s/%s)" % tuple(self.line[6:12]))

        class Charge(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getAmount(self) -> int:
                return int(self.line[3])

            def getName(self) -> int:
                return "チャージ"

        class Bus(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> int:
                return "%s: %s" % (self.line[6], self.line[8])

        class Skip(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> int:
                return "Skip"

        class Nodetail(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> int:
                return "No Details"

        class Memo(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> int:
                return self.line[12]

        @staticmethod
        def transport(line: list) -> bool:
            for i in range(6,12):
                if len(line[i]) == 0:
                    return False
            return True

        @staticmethod
        def charge(line: list) -> bool:
            for i in range(6,13):
                if len(line[i]) != 0:
                    return False
            if len(line[3]) == 0:
                return False
            return True

        @staticmethod
        def bus(line: list) -> bool:
            if line[6] != "共通":
                return False
            if not line[8][-2:] == "バス":
                return False
            return True

        @staticmethod
        def skip(line: list) -> bool:
            if line[2] != "0":
                return False
            for i in range(6,12):
                if len(line[i]) != 0:
                    return False
            return True

        @staticmethod
        def nodetail(line: list) -> bool:
            if line[2] == "0":
                return False
            for i in range(6,13):
                if len(line[i]) != 0:
                    return False
            return True

        @staticmethod
        def memo(line: list) -> bool:
            if line[2] == "0":
                return False
            if len(line[12]) <= 0:
                return False
            for i in range(6,12):
                if len(line[i]) != 0:
                    return False
            return True

        transacationTypes = {
            charge.__func__: Charge,
            skip.__func__: Skip,
            nodetail.__func__: Nodetail,
            memo.__func__: Memo,
            bus.__func__: Bus,
            transport.__func__: Transport
        }

        @staticmethod
        def _check_0(index: int, value: str) -> bool:
            return len(value) > 0 and type(value) is str and int(value) > 0

        @staticmethod
        def _check_1(index: int, value: str) -> bool:
            return len(value) == 10 and type(value) is str

        @staticmethod
        def _check_2(index: int, value: str) -> bool:
            return type(value) is str and len(value) == 0 or int(value) >= 0

        @staticmethod
        def _check_3(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_4(index: int, value: str) -> bool:
            return type(value) is str and int(value) >= 0

        @staticmethod
        def _check_5(index: int, value: str) -> bool:
            return type(value) is str and ( int(value) == 0 or int(value) == 1 )

        @staticmethod
        def _check_6(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_7(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_8(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_9(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_10(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_11(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_12(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def __new__(self, line: list, lastTransaction):
            if len(line) != 13:
                raise Exception("%d: Incorrect size of entry!" % len(line))

            for index, value in enumerate(line):
                if not getattr(self, "_check_%s" % str(index))(index, value) is True:
                    raise Exception("%d: Failed check!" % index)

            for transactionTypeFunction, transactionType in self.transacationTypes.items():
                if transactionTypeFunction(line) is True:
                    return transactionType(line, lastTransaction)

            print(line)
            raise Exception("Unable to identify type of transaction")

    def append(self, line: list):
        self.__transactions.append(Transactions.Transaction(line, self.__transactions[-1] if len(self.__transactions) != 0 else None))

    def getTransactions(self) -> 'Transactions.Transaction':
        for transaction in self.__transactions:
            yield transaction

    def __init__(self, csvFile: str):
        self.__transactions = list()
        for line in csv.reader(open(csvFile, "r", encoding='utf-8-sig')):
            if line[0] == "通番":
                self.headerTracker = Transactions.HeaderTracker(line)
                continue
            self.append(line)

        serialNumbers = set()
        self.__last_balance = None
        for transaction in self.getTransactions():
            if transaction.getSerialNumber() in serialNumbers:
                raise Exception("Double serial number detected: %d" % transaction.getSerialNumber())
            serialNumbers.add(transaction.getSerialNumber())

            if self.__last_balance is None:
                self.__last_balance = transaction.getBalance()
                continue
            if transaction.getAmount() + self.__last_balance != transaction.getBalance():
                raise Exception("Mismatching amount calculation!")
            self.__last_balance = transaction.getBalance()

        rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        for transaction in self.getTransactions():
            rowWriter.writerow(transaction.getRow())

Transactions(sys.argv[1])
