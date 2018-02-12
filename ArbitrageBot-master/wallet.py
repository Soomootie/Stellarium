#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Wallet(object):

    def __init__(self, targetBalance=0, baseBalance=0, name=""):
        self.__targetBalance = targetBalance
        self.__baseBalance = baseBalance
        self.__transition = 0.0
        self.__name = name

    def getTargetBalance(self):
        return self.__targetBalance

    def getBaseBalance(self):
        return self.__baseBalance

    def getTransition(self):
        return self.__transition

    def getName(self):
        return self.__name

    def setTargetBalance(self, newTargetBalance=0):
        """
        Set the value targetBalance to the value newTargetBalance.
        :param newTargetBalance:
        :return:
        """
        self.__targetBalance = newTargetBalance

    def setBaseBalance(self, newBaseBalance=0):
        """
        Set the value baseBalance to the value newBaseBalance.
        :param newBaseBalance:
        :return:
        """
        self.__baseBalance = newBaseBalance

    def setTransition(self, newTransition=0):
        """
        Set the value transition to the value newTransition.
        :param newTransition:
        :return:
        """
        self.__transition = newTransition
