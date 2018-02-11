#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys


def createLogger(level):
    """
        Initialize and return a logger.
        :param level:
        :return: The logger initialized.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger


def createConsoleHandler(level):
    """
        Create and return a console handler and set the level.
        :param level:
        :return: The console handler.
    """
    ch = logging.StreamHandler()
    ch.setLevel(level)
    return ch


def createFileHandler(logfile, level):
    """
        Create and return a file handler and set the level.
        :param logfile:
        :param level:
        :return: The file handler.
    """
    fh = logging.FileHandler(logfile, mode='a')
    fh.setLevel(level)
    return fh


def createFormatter():
    """
        Create and return a formatter.
        :return: The formatter.
    """
    return logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')





class Logger(object):

    def __init__(self, level, args):
        self.level = logging.getLevelName(level)
        self.logger = createLogger(level)
        self.consoleHandler = createConsoleHandler(level)
        self.fileHandler = createFileHandler(args.logfile, level)
        self.formatter = createFormatter()
        self.consoleHandler.setFormatter(self.formatter)
        self.fileHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.consoleHandler)
        self.logger.addHandler(self.fileHandler)

    def quit(self):
        self.logger.info('KeyboardInterrupt, quitting!')
        sys.exit()

    def writeError(self, buyExchange, trade, pair):
        self.logger.error('Failed to get {} {}s for {}, skipping order attempt'.format(buyExchange, trade, pair))
