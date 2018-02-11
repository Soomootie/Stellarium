#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Market(object):

    def __init__(self, baseCurrency="", targetCurrency="", separator="_", aCurrency=""):
        self.baseCurrency = baseCurrency
        self.targetCurrency = targetCurrency
        self.aCurrency = aCurrency
        self.separator = separator
        self.pair = '{}{}{}'.format(self.baseCurrency, self.separator, self.targetCurrency)
        self.aPair = '{}{}{}'.format(self.baseCurrency, self.separator, self.aCurrency)

    def getBaseCurrency(self):
        return self.baseCurrency

    def getTargetCurrency(self):
        return self.targetCurrency

    def getAcurrency(self):
        return self.aCurrency

    def getPair(self):
        return self.pair

    def getAPair(self):
        return self.aPair
