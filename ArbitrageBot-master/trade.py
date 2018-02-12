#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wallet import Wallet
from market import Market
from logger import Logger
from configparser import ConfigParser, NoSectionError


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

    def __init__(self, logger, args, market, wallet):
        if isinstance(wallet, Wallet):
            self.wallet = wallet
            self.name = wallet.name
        if isinstance(market, Market):
            self.market = market
        if isinstance(logger, Logger):
            self.publicKey, self.secretKey = loadConfigFile(logger.getLoger(), args, self.name)
            self.logger = logger.getLoger()

    def getMarket(self):
        return self.market

    def getWallet(self):
        return self.wallet

    def getPublicKey(self):
        return self.publicKey

    def getSecretKey(self):
        return self.secretKey

    def getLogger(self):
        return self.logger
