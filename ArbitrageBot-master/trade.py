#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wallet import Wallet
from market import Market
from logger import Logger
from bittrex import Bittrex
from poloniex import Poloniex
from configparser import ConfigParser, NoSectionError

trading = (Bittrex, Poloniex)


def loadConfigFile(logger, args, name=""):
    """
        Load a configuration from a file, if the file don't exist
        create a configuration file.
        :param logger:
        :param args:
        :param name:
        :return:
    """
    NAME = name.upper()
    config = ConfigParser()
    try:
        config.read(args.config)
        publicKey = config.get('ArbBot', name + 'Key')
        secretKey = config.get('ArbBot', name + 'Secret')
        args.dryrun = True
        return publicKey, secretKey
    except NoSectionError:
        logger.warning('No Config File Found! Running in Drymode!')
        args.dryrun = True
        publicKey = NAME + '_API_KEY'
        secretKey = NAME + '_API_SECRET'
        config.add_section('ArbBot')
        config.set('ArbBot', name + 'Key', publicKey)
        config.set('ArbBot', name + 'Secret', secretKey)
        try:
            with open(args.config, 'w') as configfile:
                config.write(configfile)
        except IOError:
            logger.error('Failed to create and/or write to {}'.format(args.config))
        return publicKey, secretKey


class Trade(object):

    def __init__(self, logger, args, market, wallet, api):
        if isinstance(wallet, Wallet):
            self.__wallet = wallet
            self.__name = wallet.getName()
        if isinstance(market, Market):
            self.__market = market
        if isinstance(logger, Logger):
            self.__publicKey, self.__secretKey = loadConfigFile(logger.getLoger(), args, self.__name)
            self.__logger = logger.getLoger()
        api.set_api_key(self.__publicKey)
        api.set_api_secret(self.__secretKey)
        if isinstance(api, trading):
            self.__api = api

    def getMarket(self):
        return self.__market

    def getWallet(self):
        return self.__wallet

    def getPublicKey(self):
        return self.__publicKey

    def getSecretKey(self):
        return self.__secretKey

    def getLogger(self):
        return self.__logger

    def getApi(self):
        return self.__api

    def setApi(self, api):
        assert isinstance(api, object)
        self.__api = api

    def getName(self):
        return self.__name
