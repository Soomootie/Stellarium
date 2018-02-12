#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Market(object):

    def __init__(self, baseCurrency="", targetCurrency="", separator="_", aCurrency=""):
        self.__baseCurrency = baseCurrency
        self.__targetCurrency = targetCurrency
        self.__aCurrency = aCurrency
        self.__separator = separator
        self.__pair = '{}{}{}'.format(self.__baseCurrency, self.__separator, self.__targetCurrency)
        self.__aPair = '{}{}{}'.format(self.__baseCurrency, self.__separator, self.__aCurrency)

    def getBaseCurrency(self):
        return self.__baseCurrency

    def getTargetCurrency(self):
        return self.__targetCurrency

    def getAcurrency(self):
        return self.__aCurrency

    def getPair(self):
        return self.__pair

    def getAPair(self):
        return self.__aPair
