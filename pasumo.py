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

    SERIAL_NUMBER             = 0
    DATE                      = 1
    AMOUNT                    = 3
    CHARGE_AMOUNT             = 4
    BALANCE                   = 5
    SOURCE_STATION_NAME       = 7
    SOURCE_STATION_LINE       = 8
    SOURCE_TRAIN_COMPANY      = 9
    DESTINATION_STATION_NAME  = 10
    MEMO                      = 13
    MAX_SIZE                  = 14

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
                return int(self.line[Transactions.SERIAL_NUMBER])

            def getDate(self) -> str:
                return self.line[Transactions.DATE]

            def getAmount(self) -> int:
                if self.__amount is not None:
                    return self.__amount
                if len(self.line[Transactions.AMOUNT]) > 0:
                    return -int(self.line[Transactions.AMOUNT])
                return int(self.line[Transactions.CHARGE_AMOUNT])

            def getBalance(self) -> int:
                return int(self.line[Transactions.BALANCE])

            def getName(self) -> None:
                raise Exception("%s getName should never run!" % self)

        class Transport(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> str:
                return ("%s (%s/%s) -> %s (%s/%s)" % tuple(self.line[Transactions.SOURCE_STATION_NAME:Transactions.MEMO]))

        class TransportCharge(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> str:
                return ("チャージ: %s (%s/%s)" % tuple(self.line[Transactions.SOURCE_STATION_NAME:Transactions.DESTINATION_STATION_NAME]))

        class Charge(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getAmount(self) -> int:
                return int(self.line[Transactions.CHARGE_AMOUNT])

            def getName(self) -> int:
                return "チャージ"

        class Bus(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> str:
                return "%s: %s" % (self.line[Transactions.SOURCE_STATION_NAME], self.line[Transactions.SOURCE_TRAIN_COMPANY])

        class Trafficbureau(TransactionsDetails):
            def __init__(self, line: list, lastTransaction):
                super().__init__(line, lastTransaction)

            def getName(self) -> str:
                return "%s: %s" % (self.line[Transactions.SOURCE_STATION_NAME], self.line[Transactions.SOURCE_TRAIN_COMPANY])

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
                return self.line[Transactions.MEMO]

        @staticmethod
        def transport(line: list) -> bool:
            for i in range(Transactions.SOURCE_STATION_NAME,Transactions.MEMO):
                if len(line[i]) == 0:
                    return False
            return True

        @staticmethod
        def charge(line: list) -> bool:
            for i in range(Transactions.SOURCE_STATION_NAME,Transactions.MAX_SIZE):
                if len(line[i]) != 0:
                    return False
            if len(line[Transactions.CHARGE_AMOUNT]) == 0:
                return False
            return True

        @staticmethod
        def stationcharge(line: list) -> bool:
            for i in range(Transactions.DESTINATION_STATION_NAME,Transactions.MAX_SIZE):
                if len(line[i]) != 0:
                    return False
            if len(line[Transactions.CHARGE_AMOUNT]) == 0:
                return False
            return True

        @staticmethod
        def bus(line: list) -> bool:
            if line[Transactions.SOURCE_STATION_NAME] != "共通":
                return False
            if not line[Transactions.SOURCE_TRAIN_COMPANY][-2:] == "バス":
                return False
            return True

        @staticmethod
        def trafficbureau(line: list) -> bool:
            if line[Transactions.SOURCE_STATION_NAME] != "共通":
                return False
            if not line[Transactions.SOURCE_TRAIN_COMPANY] == "東京都交通局":
                return False
            return True

        @staticmethod
        def skip(line: list) -> bool:
            if line[Transactions.AMOUNT] != "0":
                return False
            for i in range(Transactions.SOURCE_STATION_NAME,Transactions.MEMO):
                if len(line[i]) != 0:
                    return False
            return True

        @staticmethod
        def nodetail(line: list) -> bool:
            if line[Transactions.AMOUNT] == "0":
                return False
            for i in range(Transactions.SOURCE_STATION_NAME,Transactions.MAX_SIZE):
                if len(line[i]) != 0:
                    return False
            return True

        @staticmethod
        def memo(line: list) -> bool:
            if line[Transactions.AMOUNT] == "0":
                return False
            if len(line[Transactions.MEMO]) <= 0:
                return False
            for i in range(Transactions.SOURCE_STATION_LINE,Transactions.MEMO):
                if len(line[i]) != 0:
                    return False
            return True

        transacationTypes = {
            charge.__func__: Charge,
            skip.__func__: Skip,
            nodetail.__func__: Nodetail,
            memo.__func__: Memo,
            bus.__func__: Bus,
            trafficbureau.__func__: Trafficbureau,
            transport.__func__: Transport,
            stationcharge.__func__: TransportCharge,
        }

        @staticmethod
        def _check_0(index: int, value: str) -> bool:
            return len(value) > 0 and type(value) is str and int(value) > 0

        @staticmethod
        def _check_1(index: int, value: str) -> bool:
            return len(value) == 10 and type(value) is str

        @staticmethod
        def _check_2(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_3(index: int, value: str) -> bool:
            return type(value) is str and len(value) == 0 or int(value) >= 0

        @staticmethod
        def _check_4(index: int, value: str) -> bool:
            return type(value) is str

        @staticmethod
        def _check_5(index: int, value: str) -> bool:
            return type(value) is str and int(value) >= 0

        @staticmethod
        def _check_6(index: int, value: str) -> bool:
            return type(value) is str and ( int(value) == 0 or int(value) == 1 )

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
        def _check_13(index: int, value: str) -> bool:
            return type(value) is str

        def __new__(self, line: list, lastTransaction):
            if len(line) != Transactions.MAX_SIZE:
                sys.stderr.write(str(line) + "\n")
                raise Exception("%d: Incorrect size of entry!" % len(line))

            for index, value in enumerate(line):
                if not getattr(self, "_check_%s" % str(index))(index, value) is True:
                    raise Exception("%d: Failed check!" % index)

            for transactionTypeFunction, transactionType in self.transacationTypes.items():
                if transactionTypeFunction(line) is True:
                    return transactionType(line, lastTransaction)

            sys.stderr.write(str(line) + "\n")
            raise Exception("Unable to identify type of transaction")

    def append(self, line: list):
        self.__transactions.append(Transactions.Transaction(line, self.__transactions[-1] if len(self.__transactions) != 0 else None))

    def getTransactions(self) -> 'Transactions.Transaction':
        for transaction in self.__transactions:
            yield transaction

    def __init__(self, csvFile: str):
        self.__transactions = list()
        for line in csv.reader(open(csvFile, "r", encoding='utf-8-sig')):
            if line[Transactions.SERIAL_NUMBER] == "通番":
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
                sys.stderr.write(str(transaction.getRow()) + "\n")
                sys.stderr.write("Amount:" + str(transaction.getAmount()) + "\n")
                raise Exception("Mismatching amount calculation!")
            self.__last_balance = transaction.getBalance()

        rowWriter = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        rowWriter.writerow(("Txn ID", "Date", "Name", "Amount", "Balance"))
        for transaction in self.getTransactions():
            rowWriter.writerow(transaction.getRow())

        sys.stderr.write("Balance: %d\n" % self.__last_balance)

Transactions(sys.argv[1])
