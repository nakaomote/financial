#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

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

    def getName(self, name: str):
        for remove_trailing in self.remove_trailing:
            if name.startswith(remove_trailing):
                name = remove_trailing
                break

        for cut_from in self.cut_from:
            if cut_from in name:
                name = name[0:name.index(cut_from)]
                break

        return name
