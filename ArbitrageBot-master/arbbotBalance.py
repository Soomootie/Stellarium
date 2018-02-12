#!/usr/bin/env python
# -*- coding: utf-8 -*-
from utils import *
from logger import Logger
from wallet import Wallet
from market import Market
from trade import Trade
from poloniex import Poloniex
from bittrex import *

## VARIABLES STATIQUES
# rebalanced ratio
RATIO_REBALANCED = 1.03


def main():
    args = setupArgs()

    # Logger
    _Logger = Logger('DEBUG', args)
    _logger = _Logger.getLoger()

    # Markets
    bittrexMarket = Market(args.basesymbol, args.symbol, "-", args.Symbol)
    poloniexMarket = Market(args.basesymbol, args.symbol if args.symbol != "XLM" else "STR", "_", args.Symbol)

    # Wallets
    bittrexWallet = Wallet(274.69, 0.126033, BIT)  # 200$ / 200$
    poloniexWallet = Wallet(274.69, 0.0126033, POLO)  # 200$ / 200$

    bittrexAPI = Bittrex(None, None)
    poloniexAPI = Poloniex(None, None)

    bittrexTrade = Trade(_Logger, args, bittrexMarket, bittrexWallet, bittrexAPI)
    poloniexTrade = Trade(_Logger, args, poloniexMarket, poloniexWallet, poloniexAPI)

    # Log Startup Settings
    _logger.info(
        'Arb Pair: {} | Rate: {} | Interval: {} | Max Order Size: {}'.format(bittrexMarket.getPair(), args.rate,
                                                                             args.interval,
                                                                             args.max))
    if args.dryrun:
        _logger.info("Dryrun Mode Enabled (will not trade)")

    def reBalance(_buyExchange, arbitrage):

        # pas assez de btc pour acheter du xlm dans poloniex/bittrex
        if arbitrage > RATIO_REBALANCED:
            # transfert XLM polo vers XLM poloniex/bittrex
            transferTarget(bittrexTrade if _buyExchange == BIT else poloniexTrade,
                           poloniexTrade if _buyExchange == BIT else bittrexTrade)

            s_bit = bittrexAPI.get_marketsummary(bittrexMarket.getAcurrency())['result']
            s_polo = poloniexAPI.api_query(TICK)
            _logger.debug("\n{:8} : {:.8f}\n{:8} : {:.8f}".format(BIT, float(s_bit[0]['Ask']), POLO,
                                                                  float(s_polo[poloniexMarket.getAcurrency()]
                                                                        ["lowestAsk"])))

            # vend le XLM sur poloniex/bittrex
            sellTarget(bittrexTrade if _buyExchange == BIT else poloniexTrade,
                       poloniexTrade if _buyExchange == BIT else bittrexTrade)

            # !! verif le tradesize de xrp aussi
            # achète XRP poloniex/bittrex avec BTC
            buyACurrency(bittrexTrade if _buyExchange == BIT else poloniexTrade)

            # XRP poloniex/bittrex envoi vers XRP bittrex/poloniex
            sendACurrency(bittrexTrade if _buyExchange == BIT else poloniexTrade,
                          poloniexTrade if _buyExchange == BIT else bittrexTrade)

            # convert XRP poloniex/bittrex en BTC
            amountCurrency = sellACurrency(bittrexTrade if _buyExchange == BIT else poloniexTrade)
            # buy XLM with BTC on poloniex/bittrex
            buyBaseWithCurrency(amountCurrency, bittrexTrade if _buyExchange == BIT else poloniexTrade)

            _logger.info(
                "\nNouveau : \nBittrex BTC :  {:.8f} | Bittrex LUMEN: {:.8f}\nPoloniex BTC : {:.8f} | Poloniex LUMEN "
                "{:.8f}".format(bittrexWallet.getBaseBalance(), bittrexWallet.getTargetBalance(),
                                poloniexWallet.getBaseBalance(),
                                poloniexWallet.getTargetBalance()))

    ### END reBalance()

    """
        Notre stratégie suppose que le prix du XLM est plus bas sur Poloniex que sur Bittrex
        est que la différence de prix entre le BTC et XRP des 2 plates-formes est très faible
    """

    # trade simulation function
    def tradeSimulation(_buyExchange, _ask, _bid, _sellBalance, _buyBalance):

        arbitrage = _bid / _ask
        print('DEBUG: Current Rate: {} | Minimum Rate: {}'.format(arbitrage, args.rate))

        # Return if minimum arbitrage percentage is not met
        if arbitrage <= args.rate:
            return
        _sellExchange = exchange(_buyExchange)
        sellbook = sellBook(poloniexTrade if _buyExchange == POLO else bittrexTrade)
        buybook = buyBook(poloniexTrade if _buyExchange == POLO else bittrexTrade)
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
        # Fonctionnement normal du bot il achète et vend en binaire (arbitrage)
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
                "\nNouveau2 : \nBittrex BTC :  {:.8f} | Bittrex LUMEN: {:.8f}\nPoloniex BTC : {:.8f} | Poloniex LUMEN "
                "{:.8f}".format(bittrexWallet.getBaseBalance(), bittrexWallet.getTargetBalance(),
                                poloniexWallet.getBaseBalance(),
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
            _Logger.quit()
        except KeyError:
            traceback.print_exc()
            _logger.error('Failed to Query Poloniex API, Restarting Loop')
            continue
        poloBid = float(currentValues[poloniexMarket.getPair()]["highestBid"])
        poloAsk = float(currentValues[poloniexMarket.getPair()]["lowestAsk"])

        # Query Bittrex Prices

        try:
            summary = bittrexAPI.get_marketsummary(bittrexMarket.getPair())['result'][0]
            print(summary)

        except KeyboardInterrupt:
            _Logger.quit()

        except KeyError:
            traceback.print_exc()
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
