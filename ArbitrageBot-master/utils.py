#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import time
from trade import Trade

POLO = 'Poloniex'
BIT = 'Bittrex'
SEC = 3


def setupArgs():
    """
        Setup Argument Parser.
        Return the arguments.
    """
    parser = argparse.ArgumentParser(description='Poloniex/Bittrex Arbitrage Bot')
    parser.add_argument('-s', '--symbol', default='XRP', type=str, required=False,
                        help='symbol of your target coin [default: ?]')
    parser.add_argument('-b', '--basesymbol', default='BTC', type=str, required=False,
                        help='symbol of your base coin [default: BTC]')
    parser.add_argument('-S', '--Symbol', default='XLM', type=str, required=False,
                        help='symbol of you second target coin [default: ?]')
    parser.add_argument('-r', '--rate', default=1.0005, type=float, required=False,
                        help='minimum price difference, 1.01 is 1 percent price difference [default: 1.01]')
    parser.add_argument('-m', '--max', default=0.0, type=float, required=False,
                        help='maximum order size in target currency (0.0 is unlimited) [default: 0.0]')
    parser.add_argument('-i', '--interval', default=1, type=int, required=False,
                        help='seconds to sleep between loops [default: 1]')
    parser.add_argument('-c', '--config', default='arbbot.conf', type=str, required=False,
                        help='config file [default: arbbot.conf]')
    parser.add_argument('-l', '--logfile', default='arbbot.log', type=str, required=False,
                        help='file to output log data to [default: arbbot.log]')
    parser.add_argument('-d', '--dryrun', action='store_true', required=False,
                        help='simulates without trading (API keys not required)')
    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                        help='enables extra console messages (for debugging)')
    return parser.parse_args()


def exchange(_buyExchange):
    return POLO if _buyExchange != POLO else BIT


def setTradesize(newTradesize):
    global tradesize
    tradesize = newTradesize


def getTradesize():
    return tradesize


def transferInfo(currency, trade, receiver):
    if isinstance(trade, Trade):
        trade.getLogger().warning(
            "Transfert de {:12.8f} {:3} de {} vers {}".format(trade.getWallet().getTargetBalance(), currency,
                                                              trade.getWallet().getName(), receiver))


def transferTarget(_buyExchange, trade, trade1):
    if isinstance(trade, Trade) and isinstance(trade1, Trade):
        setTradesize(trade.getWallet().getTargetBalance())
        trade1.getWallet().setTargetBalance(trade1.getWallet().getTargetBalance() + getTradesize())
        trade.getWallet().setTargetBalance()
        time.sleep(SEC)  # durée de l'envoi d'un portefeuille à un autre
        transferInfo(trade1.getWallet().getTargetCurrency(), trade1.getWallet().getTargetBalance(),
                     BIT if _buyExchange == BIT else POLO)


def sellBook(_buyExchange):
    if _buyExchange == POLO:
        try:
            print("IN SELL BOOK !")
            return poloBook('asks')
        except KeyboardInterrupt:
            _Logger.quit()
        except KeyError:
            traceback.print_exc()
            _logger.writeError(POLO, 'Ask', poloniexMarket.getPair())
            return None
    if _buyExchange == BIT:
        try:
            print(bitBook('sell'))
            return bitBook('sell')
        except KeyboardInterrupt:
            _Logger.quit()
        except KeyError:
            traceback.print_exc()
            _logger.writeError(BIT, 'Bid', bittrexMarket.getPair())
            return None
