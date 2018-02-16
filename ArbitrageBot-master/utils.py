#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import time
import traceback

from trade import Trade
from bittrex import Bittrex
from poloniex import Poloniex

POLO = 'Poloniex'
BIT = 'Bittrex'
SEC = 3
tradesize = 0

TICK = 'returnTicker'


def setupArgs():
    """
        Setup Argument Parser.
        Return the arguments.
    """
    parser = argparse.ArgumentParser(description='Poloniex/Bittrex Arbitrage Bot')
    parser.add_argument('-s', '--symbol', default='STORJ', type=str, required=False,
                        help='symbol of your target coin [default: ?]')
    parser.add_argument('-b', '--basesymbol', default='BTC', type=str, required=False,
                        help='symbol of your base coin [default: BTC]')
    parser.add_argument('-S', '--Symbol', default='XRP', type=str, required=False,
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


def setTradesize(newTradesize=0):
    global tradesize
    tradesize = newTradesize


def getTradesize():
    return tradesize


def transferInfo(currency, trade, receiver):
    if isinstance(trade, Trade):
        trade.getLogger().warning(
            "Transfert de {:12.8f} {:3} de {} vers {}".format(getTradesize(), currency,
                                                              trade.getWallet().getName(), receiver))


def transferTarget(sender_trade: Trade, receiver_trade: Trade):
    setTradesize(sender_trade.getWallet().getTargetBalance())
    receiver_trade.getWallet().setTargetBalance(receiver_trade.getWallet().getTargetBalance() + getTradesize())
    sender_trade.getWallet().setTargetBalance()
    time.sleep(SEC)  # durée de l'envoi d'un portefeuille à un autre
    transferInfo(sender_trade.getMarket().getTargetCurrency(), sender_trade, receiver_trade.getName())


def book(_trade, trade: Trade):
    if isinstance(trade.getApi(), Poloniex):
        return trade.getApi().returnOrderBook(trade.getMarket().getPair())[_trade][0][1]
    elif isinstance(trade.getApi(), Bittrex):
        return trade.getApi().get_orderbook(trade.getMarket().getPair())['result'][_trade][0]['Quantity']


def sellBook(trade):
    try:
        return book('asks' if trade.getName() == POLO else 'sell', trade)
    except KeyboardInterrupt:
        trade.getLogger().quit()
    except KeyError:
        traceback.print_exc()
        trade.getLogger().writeError(trade.getName(), 'Ask' if trade.getName() == POLO else 'Bid', trade.getPair())
        return None


def buyBook(trade):
    try:
        return book('buy' if trade.getName() == BIT else 'bids', trade)
    except KeyboardInterrupt:
        trade.getLogger().quit()
    except KeyError or TypeError:
        traceback.print_exc()
        trade.getLogger().writeError(trade.getName(), 'Ask' if trade.getName() == BIT else 'Bid', trade.getPair())
        return None


def getMarket(trade: Trade):
    if isinstance(trade.getApi(), Bittrex):
        return trade.getApi().get_marketsummary(trade.getMarket().getPair())['result']
    elif isinstance(trade.getApi(), Poloniex):
        return trade.getApi().returnTicker()


def getMarkets(trade: Trade):
    if isinstance(trade.getApi(), Bittrex):
        return trade.getApi().get_market_summaries()
    if isinstance(trade.getApi(), Poloniex):
        return trade.getApi().returnTicker()


def getPrice(market, pair):
    try:
        return market[0]['Ask']
    except:
        return float(market[pair]['lowestAsk'])


def tradeInfo(trade: str, currency: str, _trade: Trade, amount, price):
    total = amount * price
    trade = "Vente" if trade == "sell" else "Achat"
    _trade.getLogger().critical(
        "{:^8} de {:12.8f} {:3} @ {:.8f} {} sur {:8} => {:.8f} {}".format(trade, amount, currency, price
                                                                          , _trade.getMarket().getBaseCurrency(),
                                                                          _trade.getName(),
                                                                          total, _trade.getMarket().getBaseCurrency()))


def sellTarget(buy_trade: Trade, sell_trade: Trade):
    summary = getMarket(sell_trade)
    price = getPrice(summary, sell_trade.getMarket().getPair())
    amount = getTradesize()
    sell_trade.getWallet().setTargetBalance(sell_trade.getWallet().getTargetBalance() - getTradesize())
    setTradesize(amount * price)
    sell_trade.getWallet().setBaseBalance(sell_trade.getWallet().getBaseBalance() + getTradesize())
    tradeInfo('sell', sell_trade.getMarket().getTargetCurrency(), buy_trade, amount, price)


def buyACurrency(trade: Trade):
    _summary = getMarket(trade)
    price = getPrice(_summary, trade.getMarket().getPair())
    trade.getWallet().setBaseBalance(trade.getWallet().getBaseBalance() - getTradesize())
    setTradesize(getTradesize() / price)
    trade.getWallet().setTransition(trade.getWallet().getTransition() + getTradesize())
    tradeInfo('buy', trade.getMarket().getTargetCurrency(), trade, getTradesize(), price)


def sendACurrency(sender_trade: Trade, receiver_trade: Trade):
    transferInfo(sender_trade.getMarket().getAcurrency(), sender_trade.getWallet().getTransition(),
                 receiver_trade.getName())
    sender_trade.getWallet().setTransition(sender_trade.getWallet().getTransition() - getTradesize())
    receiver_trade.getWallet().setTransition(receiver_trade.getWallet().getTransition() + getTradesize())
    time.sleep(SEC)


def sellACurrency(trade: Trade):
    _summary = getMarket(trade)
    price = getPrice(_summary, trade.getMarket().getPair())
    sellCurrencyToBase = price * trade.getWallet().getTransition()
    trade.getWallet().setBaseBalance(trade.getWallet().getBaseBalance() + sellCurrencyToBase)
    trade.getWallet().setTransition()
    setTradesize()
    return sellCurrencyToBase


def buyBaseWithCurrency(amount, trade: Trade):
    _summary = getMarket(trade)
    price = getPrice(_summary, trade.getMarket().getAPair())
    _amount = amount / price
    trade.getWallet().setTargetBalance(trade.getWallet().getTargetBalance() + _amount)
    tradeInfo('buy', trade.getMarket().getTargetCurrency(), trade, _amount, price)
    trade.getWallet().setBaseBalance(trade.getWallet().getBaseBalance() - amount)


def sames(trade: Trade, trade1: Trade, logger):
    result = []
    summary = getMarkets(trade)
    summary1 = getMarkets(trade1)
    for i in summary1:
        for j in summary['result']:
            i_res = i.split('_')
            j_res = j['MarketName'].split('-')
            if i_res[1] == j_res[1]:
                write = True
                for k in result:
                    if k == i_res[1]:
                        write = False
                        continue
                if write:
                    result.append(i_res[1])
                    logger.info("{}".format(i_res[1]))
