#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run everything.
"""

from neobank import neobankAll
from sony import sonyAll
import os
from dataclasses import dataclass
from typing import Callable
import io
from contextlib import redirect_stdout
from typing import Union, List

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

def doRun(run: bankRun) -> Union[str, None]:
    if os.path.isfile(run.filename):
        return None
    run.download()
    f = io.StringIO()
    with redirect_stdout(f):
        run.parse()
    with open(run.filename, "w") as rb:
            rb.write(f.getvalue())
    print(f"Created {run.filename}")
    return run.filename

if __name__ == '__main__':
    uploadDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
    def flattenRuns(runs: list[Callable[[str], list[bankRun]]]) -> List[Union[str, None]]:
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
                    neobankAll,
                    vpassAll,
                    mobilePasumoAll,
                    jnbAll,
                    sevenAll,
                    rakutenAll,
                    sonyAll,
                    ufjAll,
                    oliveAll,
                ])
        ))

    print("\n".join(runs))
