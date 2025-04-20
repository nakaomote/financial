#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Callable

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Descriptions(metaclass=Singleton):


    def __init__(self):
        with open("modifications.json", "r") as config_file:
            config = json.load(config_file)
            self.remove_trailing = config.pop("remove_trailing")
            self.cut_from = config.pop("cut_from")
            self.substitutions = config.pop("substitutions")

        self.__functions = (
            self.__removeTrailing,
            self.__cutFrom,
            self.__substitution,
        )


    def __removeTrailing(self, name: str) -> str:
        remove_trailing: str
        for remove_trailing in self.remove_trailing:
            if name.startswith(remove_trailing):
                return remove_trailing
        return name

    def __cutFrom(self, name: str) -> str:
        for cut_from in self.cut_from:
            if cut_from in name:
                return name[0:name.index(cut_from)]
        return name

    def __substitution(self, name: str) -> str:
        for f, t in self.substitutions.items():
            if f in name:
                return name.replace(f,t)
        return name

    def __runFunctions(self, n: int, name: str) -> str:
        if n - 1 <= 0:
            return self.__functions[n-1](name)
        return self.__runFunctions(n-1, self.__functions[n-1](name))

    def getName(self, name: str):
        return self.__runFunctions(n=len(self.__functions), name=name)
