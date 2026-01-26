#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run everything.
"""

import csv
from neobank import neobankAll
from sony import sonyAll
import os
from dataclasses import dataclass
from typing import Callable
import io
from contextlib import redirect_stdout
from typing import List

from ufj import ufjAll
from rakuten import rakutenAll
from seven import sevenAll
from jnb import jnbAll
from olive import oliveAll
from vpass import vpassAll
from mobilePasumo import mobilePasumoAll

@dataclass
class bankRun:
    filename: str
    download: Callable
    parse: Callable
    finalBalance: Callable[[], dict[str,int]]

@dataclass
class bankRunResult:
    bankRun: bankRun
    wasRun: bool

def doRun(run: bankRun) -> bankRunResult:
    if os.path.isfile(run.filename):
        return bankRunResult(
            bankRun = run,
            wasRun  = False,
        )
    run.download()
    f = io.StringIO()
    with redirect_stdout(f):
        run.parse()
    with open(run.filename, "w") as rb:
            rb.write(f.getvalue())
    print(f"Created {run.filename}")
    return bankRunResult(
        bankRun = run,
        wasRun  = True,
    )

def showCreated(runs: list[bankRunResult]):
    created = list(
        filter( lambda result: result.wasRun, runs)
    )
    if len(created) == 0:
        return
    print("\ncreated overall:\n\n" + "\n".join(
            map(lambda result: result.bankRun.filename, created)
        )
    )

def showFinalBalances(runs: list[bankRunResult]):
    print("\naccount balances:\n")
    with open(os.path.join(uploadDir, "balances.csv"), "w") as rb:
        stdoutRowWriter = csv.writer(rb, delimiter=',', quotechar='"')
        for run in runs:
            balanceAmounts = run.bankRun.finalBalance()
            for name, balance in balanceAmounts.items():
                print("%s: %s" % (name, balance))
                stdoutRowWriter.writerow((name, balance,))

if __name__ == '__main__':
    uploadDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
    def flattenRuns(runs: list[Callable[[str], list[bankRun]]]) -> List[bankRunResult]:
        if len(runs) == 0:
            return []
        return list(
                    map(
                        doRun,
                        runs[0](uploadDir)
                    )
                ) + flattenRuns(runs[1:])

    runs = \
        list(
            filter(
                None,
                flattenRuns([
                    vpassAll,
                    ufjAll,
                    sevenAll,
                    rakutenAll,
                    jnbAll,
                    sonyAll,
                    neobankAll,
                    mobilePasumoAll,
                    oliveAll,
                ])
        ))

    showCreated(runs)
    showFinalBalances(runs)
