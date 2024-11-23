#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Run everything.
"""

from os.path import isfile
from sony import sonyAll
import os
from dataclasses import dataclass
from typing import Callable
import io
from contextlib import redirect_stdout
from typing import Union, List

@dataclass
class bankRun:
    filename: str
    download: Callable
    parse: Callable

def doRun(run: bankRun) -> Union[str, None]:
    if not os.path.isfile(run.filename):
        run.download()
        f = io.StringIO()
        with redirect_stdout(f):
            run.parse()
        with open(run.filename, "w") as rb:
                rb.write(f.getvalue())
        return run.filename
    return None

def flattenRuns(runs: Union[List[List[bankRun] | bankRun],List[bankRun]]) -> List[Union[str, None]]:
    return (
            flattenRuns(runs[0])
                if isinstance(runs[0], list) else
            [doRun(runs[0])]
        ) + flattenRuns(runs[1:]) if len(runs) > 0 else []

if __name__ == '__main__':
    uploadDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')

    runs = \
        list(
            filter(
                None,
                flattenRuns([
                    sonyAll(uploadDir),
                ])
        ))

    print("\n".join(runs))
