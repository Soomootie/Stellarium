#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Wallet(object):

    def __init__(self, targetBalance=0, baseBalance=0, name=""):
        self.targetBalance = targetBalance
        self.baseBalance = baseBalance
        self.transition = 0
        self.name = name

    def getTargetBalance(self):
        return self.targetBalance

    def getBaseBalance(self):
        return self.baseBalance

    def getTransition(self):
        return self.transition

    def getName(self):
        return self.name

    def setTargetBalance(self, newTargetBalance=0):
        """
        Set the value targetBalance to the value newTargetBalance.
        :param newTargetBalance:
        :return:
        """
        self.targetBalance = newTargetBalance

    def setBaseBalance(self, newBaseBalance=0):
        """
        Set the value baseBalance to the value newBaseBalance.
        :param newBaseBalance:
        :return:
        """
        self.baseBalance = newBaseBalance

    def setTransition(self, newTransition=0):
        """
        Set the value transition to the value newTransition.
        :param newTransition:
        :return:
        """
        self.transition = newTransition
