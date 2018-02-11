#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Imports
import argparse
import sys
import logger
from wallet import Wallet
from market import Market
from trade import Trade

from poloniex import Poloniex
from bittrex import *

### END imports

## VARIABLES STATIQUES
# rebalanced ratio
RATIO_REBALANCED = 1.03

# site name
POLO = 'Poloniex'
BIT = 'Bittrex'

TICK = 'returnTicker'

SEC = 3


### END Variables statiques

def setupArgs():
    """
        Setup Argument Parser.
        Return the arguments.
    """
    parser = argparse.ArgumentParser(description='Poloniex/Bittrex Arbitrage Bot')
    parser.add_argument('-s', '--symbol', default='XLM', type=str, required=False,
                        help='symbol of your target coin [default: XLM]')
    parser.add_argument('-b', '--basesymbol', default='BTC', type=str, required=False,
                        help='symbol of your base coin [default: BTC]')
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


def main():
    # global _buyExchange, tradesize

    def setTradesize(newTradesize):
        global tradesize
        tradesize = newTradesize

    def getTradesize():
        return tradesize

    args = setupArgs()

    Acurrency = 'XRP'
    bittrexMarket = Market(args.basesymbol, args.symbol, Acurrency)
    poloniexMarket = Market(args.basesymbol, args.symbol if args.symbol != "XLM" else "STR", Acurrency, "-")

    # Wallets
    bittrexWallet = Wallet(274.69, 0.126033)  # 200$ / 200$
    poloniexWallet = Wallet(274.69, 0.0126033)  # 200$ / 200$

    bittrexTrade = Trade(logger, args, bittrexMarket, bittrexWallet)
    poloniexTrade = Trade(logger, args, poloniexMarket, poloniexWallet)

    w = bittrexTrade.getMarket()

    Logger = logger.Logger('DEBUG', args)
    _logger = Logger.logger

    # Log Startup Settings
    _logger.info(
        'Arb Pair: {} | Rate: {} | Interval: {} | Max Order Size: {}'.format(bittrexMarket.getPair(), args.rate,
                                                                             args.interval,
                                                                             args.max))
    if args.dryrun:
        _logger.info("Dryrun Mode Enabled (will not trade)")

    bittrexAPI, poloniexAPI = Bittrex(bittrexTrade.publicKey, bittrexTrade.secretKey), Poloniex(poloniexTrade.publicKey,
                                                                                                poloniexTrade.secretKey)

    def reBalance(_buyExchange, arbitrage):

        def exchange(_buyExchange=_buyExchange):
            """
                Return the "opposite" of _buyExchange.
            """
            return POLO if _buyExchange != POLO else BIT

        ### END exchange()

        def transferInfo(currency, trade : Trade, receiver):
            _logger.warning(
                "Transfert de {:12.8f} {:3} de {} vers {}".format(targetBalance, (trade.getMarket()), receiver, receiver))

        ### END transferInfo

        def tradeInfo(currency, trade, sender, amount, price):
            _exchange = exchange(sender)
            total = amount * price
            trade = "Vente" if trade == "sell" else "Achat"
            _logger.critical(
                "{:^8} de {:12.8f} {:3} @ {:.8f} {} sur {:8} => {:.8f} {}".format(trade, amount, currency, price
                                                                                  , getBaseCurrency(args), _exchange,
                                                                                  total, getBaseCurrency(args)))

        ### END tradeInfo()

        def transferTarget():
            if _buyExchange == POLO:
                setTradesize(poloniexWallet.getTargetBalance())
                bittrexWallet.setTargetBalance(bittrexWallet.getTargetBalance() + getTradesize())
                poloniexWallet.setTargetBalance()
                time.sleep(SEC)  # duree de l'envoi d'un portefeuille à un autre
                transferInfo(bittrexMarket.getTargetCurrency(), bittrexWallet.getTargetBalance(), BIT)
            if _buyExchange == BIT:
                setTradesize(bittrexWallet.getTargetBalance())
                poloniexWallet.setTargetBalance(poloniexWallet.getTargetBalance() + getTradesize())
                bittrexWallet.setTargetBalance()
                time.sleep(SEC)  # duree de l'envoi d'un portefeuille à un autre
                transferInfo(poloniexMarket.getTargetCurrency(), poloniexWallet.getTargetBalance(), POLO)

        ### END transferTarget()

        def sellTarget():
            if _buyExchange == POLO:
                _summary = bittrexAPI.get_marketsummary(bittrexMarket.getPair())['result']
                price = _summary[0]['Ask']
                amount = getTradesize()
                bittrexWallet.setTargetBalance(
                    bittrexWallet.getTargetBalance() - getTradesize())  # tradesize in target currency
                setTradesize(amount * price)  # tradesize in base currency
                bittrexWallet.setBaseBalance(bittrexWallet.getBaseBalance() + getTradesize())
                tradeInfo(poloniexMarket.targetCurrency, 'sell', POLO, amount, price)
            if _buyExchange == BIT:
                _summary = poloniexAPI.api_query(TICK)
                price = float(_summary[poloniexMarket.getPair()]["lowestAsk"])
                amount = getTradesize()
                poloniexWallet.setTargetBalance(poloniexWallet.getTargetBalance() - getTradesize())
                setTradesize(amount * price)
                poloniexWallet.setBaseBalance(poloniexWallet.getBaseBalance() + getTradesize())
                tradeInfo(bittrexMarket.getTargetCurrency(), 'sell', BIT, amount, price)

        ### END sellTarget()

        def buyACurrency(currency):
            if _buyExchange == POLO:
                _summary = bittrexAPI.get_marketsummary(bittrexMarket.getPair())['result'][0]
                price = float(_summary['Ask'])
                bittrexWallet.setBaseBalance(bittrexWallet.getBaseBalance() - getTradesize())  # tradesize in currency
                setTradesize(getTradesize() / price)
                bittrexWallet.setTransition(bittrexWallet.getTransition() + getTradesize())
                _logger.debug("{:.8f}".format(price))
                tradeInfo(currency, 'buy', POLO, getTradesize(), price)
            if _buyExchange == BIT:
                _summary = poloniexAPI.api_query(TICK)
                price = float(_summary[poloniexMarket.getPair()]["lowestAsk"])
                poloniexWallet.setBaseBalance(poloniexWallet.getBaseBalance() - getTradesize())
                setTradesize(getTradesize() / price)
                poloniexWallet.setTransition(poloniexWallet.getTransition() + getTradesize())
                tradeInfo(currency, 'buy', BIT, getTradesize(), price)

        ### END buyACurrency()

        def sendACurrency(currency):
            if _buyExchange == POLO:
                transferInfo(currency, bittrexWallet.getTransition(), POLO)
                bittrexWallet.setTransition(bittrexWallet.getTransition() - getTradesize())
                poloniexWallet.setTransition(poloniexWallet.getTransition() + getTradesize())
                time.sleep(SEC)
            if _buyExchange == BIT:
                transferInfo(currency, poloniexWallet.getTransition(), BIT)
                poloniexWallet.setTransition(poloniexWallet.getTransition() - getTradesize())
                bittrexWallet.setTransition(bittrexWallet.getTransition() + getTradesize())
                time.sleep(SEC)

        ### END sendACurrency()

        def sellACurrency(currency):
            if _buyExchange == POLO:
                _summary = poloniexAPI.api_query(TICK)
                print(_summary)
                price = float(_summary[poloniexMarket.getAcurrency()]["lowestAsk"])
                sellCurrencyToBase = price * poloniexWallet.getTransition()
                poloniexWallet.setBaseBalance(poloniexWallet.getBaseBalance() + sellCurrencyToBase)
                tradeInfo(currency, 'sell', BIT, poloniexWallet.getTransition(), price)
                poloniexWallet.setTransition(0)
                setTradesize(0)
                return sellCurrencyToBase
            if _buyExchange == BIT:
                _summary = bittrexAPI.get_marketsummary(bittrexMarket.getAcurrency())['result'][0]
                price = float(_summary['Ask'])
                sellCurrencyToBase = price * bittrexWallet.getTransition()
                bittrexWallet.setBaseBalance(bittrexWallet.getBaseBalance() + sellCurrencyToBase)
                tradeInfo(currency, 'sell', POLO, bittrexWallet.getTransition(), price)
                bittrexWallet.setTransition(0)
                setTradesize(0)
                return sellCurrencyToBase

        ### END sellACurrency()

        def buyBaseWithCurrency(amount, currency):
            if _buyExchange == POLO:
                _summary = poloniexAPI.api_query(TICK)
                price = float(_summary[poloniexMarket.getPair()]["lowestAsk"])
                poloniexWallet.setTargetBalance(poloniexWallet.getTargetBalance() + amount / price)
                tradeInfo(currency, 'buy', BIT, amount / price, price)
                poloniexWallet.setBaseBalance(poloniexWallet.getBaseBalance() - amount)
            if _buyExchange == BIT:
                _summary = bittrexAPI.get_marketsummary(bittrexMarket.getPair())['result'][0]
                price = float(_summary['Ask'])
                _logger.debug("OOPS")
                bittrexWallet.setTargetBalance(bittrexWallet.getTargetBalance() + amount / price)
                tradeInfo(currency, 'buy', POLO, amount / price, price)
                bittrexWallet.setBaseBalance(bittrexWallet.getBaseBalance() - amount)

        ### END buyBaseWithCurrency()

        # def temp() :

        # pas assez de btc pour acheter du xlm dans poloniex/bittrex
        if arbitrage > RATIO_REBALANCED:
            # transfert XLM polo vers XLM poloniex/bittrex
            transferTarget()

            s_bit = bittrexAPI.get_marketsummary(bittrexMarket.getAcurrency())['result']
            s_polo = poloniexAPI.api_query(TICK)
            _logger.debug("\n{:8} : {:.8f}\n{:8} : {:.8f}".format(BIT, float(s_bit[0]['Ask']), POLO,
                                                                  float(s_polo[poloniexMarket.getAcurrency()][
                                                                            "lowestAsk"])))

            # vend le XLM sur poloniex/bittrex
            sellTarget()

            # !! verif le tradesize de xrp aussi
            # achete XRP poloniex/bittrex avec BTC
            buyACurrency(Acurrency)

            # XRP poloniex/bittrex envoi vers XRP bittrex/poloniex
            sendACurrency(Acurrency)

            # convert XRP poloniex/bittrex en BTC
            amountCurrency = sellACurrency(Acurrency)
            # buy XLM with BTC on poloniex/bittrex
            buyBaseWithCurrency(amountCurrency, bittrexMarket.getTargetCurrency())

            _logger.info(
                "\nNouveau : \nBittrex BTC :  {:.8f} | Bittrex LUMEN: {:.8f}\nPoloniex BTC : {:.8f} | Poloniex LUMEN {:.8f}".format(
                    bittrexWallet.getBaseBalance(), bittrexWallet.getTargetBalance(), poloniexWallet.getBaseBalance(),
                    poloniexWallet.getTargetBalance()))

    ### END reBalance()

    """
        Notre statégie suppose que le prix du XLM est plus bas sur Poloniex que sur Bittrex
        est que la différence de prix entre le BTC et XRP des 2 plateformes est très faible
    """

    # trade simulation function
    def tradeSimulation(_buyExchange, _ask, _bid, _sellBalance, _buyBalance):
        def exchange(_buyExchange=_buyExchange):
            """
                Return the "opposite" of _buyExchange.
            """
            return POLO if _buyExchange != POLO else BIT

        ### END exchange()

        arbitrage = _bid / _ask
        print('DEBUG: Current Rate: {} | Minimum Rate: {}'.format(arbitrage, args.rate))

        def bitBook(trade):
            return bittrexAPI.get_orderbook(bittrexMarket.getPair())['result'][trade][0]["Quantity"]

        ### END bitBook()

        def poloBook(trade):
            return poloniexAPI.returnOrderBook(poloniexMarket.getPair())[trade][0][1]

        ### END bitBook()

        def sellBook():
            if _buyExchange == POLO:
                try:
                    print("IN SELL BOOK !")
                    return poloBook('asks')
                except KeyboardInterrupt:
                    Logger.quit()
                except:
                    print("ERROR :", sys.exc_info()[0])
                    _logger.writeError(POLO, 'Ask', poloniexMarket.getPair())
                    return None
            if _buyExchange == BIT:
                try:
                    print(bitBook('sell'))
                    return bitBook('sell')
                except KeyboardInterrupt:
                    Logger.quit()
                except:
                    print("ERROR :", sys.exc_info()[0])
                    _logger.writeError(BIT, 'Bid', bittrexMarket.getPair())
                    return None

        ### END sellBook()

        def buyBook():
            if _buyExchange == POLO:
                try:
                    return bitBook('buy')['Quantity']
                except KeyboardInterrupt:
                    Logger.quit()
                except:
                    _logger.writeError(BIT, 'Ask', bittrexMarket.getPair())
                    return None
            if _buyExchange == BIT:
                try:
                    return poloBook('bids')
                except KeyboardInterrupt:
                    Logger.quit()
                except:
                    _logger.writeError(POLO, 'Bid', poloniexMarket.getPair())
                    return None

        ### END buyBook()

        # Return if minimum arbitrage percentage is not met
        if arbitrage <= args.rate:
            return
        _sellExchange = exchange()
        sellbook = sellBook()
        buybook = buyBook()
        print("Buybook {}\n Sellbook {}".format(buybook, sellbook))
        sellbook = 0 if sellbook is None else sellbook
        buybook = 0 if buybook is None else buybook

        _logger.info(
            'OPPORTUNITY: BUY @ ' + _buyExchange + ' | SELL @ ' + _sellExchange + ' | RATE: ' + str(arbitrage) + '%')

        # Find minimum order size
        setTradesize(min(sellbook, buybook))

        # Setting order size in case balance not enough
        if _sellBalance < getTradesize():
            _logger.info('Tradesize ({}) larger than sell balance ({} @ {}), lowering tradesize.'.format(getTradesize(),
                                                                                                         _sellBalance,
                                                                                                         _sellExchange))
            setTradesize(_sellBalance)

        if (getTradesize() * _ask) > _buyBalance:
            newTradesize = _buyBalance / _ask
            _logger.info(
                'Tradesize ({}) larger than buy balance ({} @ {}), lowering tradesize to {}.'.format(getTradesize(),
                                                                                                     _buyBalance,
                                                                                                     _buyExchange,
                                                                                                     newTradesize))
            setTradesize(newTradesize)

        # Check if above min order size
        # Fonctionnement normal du bot il achete et vend en binaire (arbitrage)
        if (getTradesize() * _bid) > 0.0006001:  # less than 10$

            _logger.info(
                "ORDER {}\nSELL: {}	| {} @ {:.8f} (Balance: {})\nBUY: {}	| {} @ {:.8f} (Balance: {})".format(
                    bittrexMarket.getPair(), _sellExchange, getTradesize(), _bid, _sellBalance, _buyExchange,
                    getTradesize(), _ask,
                    _buyBalance))

            # Execute order
            # Wallet simulation
            if _buyExchange == POLO:
                # Sell on Bittrex
                bittrexWallet.setTargetBalance(bittrexWallet.getTargetBalance() - getTradesize())
                bittrexWallet.setBaseBalance(bittrexWallet.getBaseBalance() + (getTradesize() * _bid))
                # Buy on Poloniex
                poloniexWallet.setBaseBalance(poloniexWallet.getBaseBalance() - (getTradesize() * _ask))
                poloniexWallet.setTargetBalance(poloniexWallet.getTargetBalance() + getTradesize())
            elif _buyExchange == BIT:
                # Buy on Bittrex
                bittrexWallet.setTargetBalance(bittrexWallet.getTargetBalance() + getTradesize())
                bittrexWallet.setBaseBalance(bittrexWallet.getBaseBalance() - (getTradesize() * _ask))
                # Sell on Poloniex
                poloniexWallet.setBaseBalance(poloniexWallet.getBaseBalance() + (getTradesize() * _bid))
                poloniexWallet.setTargetBalance(poloniexWallet.getTargetBalance() - getTradesize())

            _logger.info(
                "\nNouveau2 : \nBittrex BTC :  {:.8f} | Bittrex LUMEN: {:.8f}\nPoloniex BTC : {:.8f} | Poloniex LUMEN {:.8f}".format(
                    bittrexWallet.getBaseBalance(), bittrexWallet.getTargetBalance(), poloniexWallet.getBaseBalance(),
                    _sellBalance))
            _logger.info("Dryrun: skipping order")

        # pas assez pour acheter du XLM
        else:
            reBalance(_buyExchange, arbitrage)
            _logger.warning("Order size not above min order size, no trade was executed")

    i = 1
    # Main Loop
    while True:
        if i == 20:
            time.sleep(SEC)
            exit()
        i += 1
        print("=================DEBUT=====================")
        # Query Poloniex Prices
        try:
            currentValues = poloniexAPI.api_query(TICK)
            print(currentValues[poloniexMarket.getPair()])
        except KeyboardInterrupt:
            Logger.quit()
        except:
            _logger.error('Failed to Query Poloniex API, Restarting Loop')
            continue
        poloBid = float(currentValues[poloniexMarket.getPair()]["highestBid"])
        poloAsk = float(currentValues[poloniexMarket.getPair()]["lowestAsk"])

        # Query Bittrex Prices

        try:
            summary = bittrexAPI.get_marketsummary(bittrexMarket.getPair())['result'][0]
            print(summary)

        except KeyboardInterrupt:
            Logger.quit()

        except:
            _logger.error('Failed to Query Bittrex API, Restarting Loop')
            continue

        bittrexAsk = summary['Ask']
        bittrexBid = summary['Bid']

        # Buy from Polo, Sell to Bittrex
        if poloAsk < bittrexBid:
            print("Polo achat ?")
            tradeSimulation(POLO, poloAsk, bittrexBid, bittrexWallet.getTargetBalance(),
                            poloniexWallet.getBaseBalance())
        # Sell to polo, Buy from Bittrex
        if bittrexAsk < poloBid:
            print("Polo vente ?")
            tradeSimulation(BIT, bittrexAsk, poloBid, poloniexWallet.getTargetBalance(), bittrexWallet.getBaseBalance())

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
