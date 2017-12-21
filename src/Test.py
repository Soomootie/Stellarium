import time

from bittrex.bittrex import Bittrex, API_V1_1
from poloniex import Poloniex
from binance.client import Client

import Keys
import datetime

API = API_V1_1
DATE = datetime.datetime.now()
TRADE = ''
POLONIEX = 'POLONIEX'
BITTREX = 'BITTREX'
FORMAT = '{0:.8f}'
_MARGIN = 0.00000001


def poloniex(market = 'BTC_STR') :
    polo = Poloniex();
    ticket_poloniex = polo.returnTicker()[market]
    print("Ask : " + FORMAT.format(ticket_poloniex['lowestAsk'])
          + " Bid : " + FORMAT.format(ticket_poloniex['highestBid']))
    return float(ticket_poloniex['lowestAsk']) , float(ticket_poloniex['highestBid'])
    
def bittrex(market = 'BTC-XLM') :
    global API
    bittrex = Bittrex(None, None, api_version = API)
    ticket_bittrex = bittrex.get_ticker(market)['result']
    print("Ask : " + FORMAT.format(ticket_bittrex['Ask'])
          + " Bid : " + FORMAT.format(ticket_bittrex['Bid']))
    ask_Bittrex = ticket_bittrex['Ask']
    bid_Bittrex = ticket_bittrex['Bid']
    return ask_Bittrex, bid_Bittrex

def _buy(_file, ask, bid, margin, trader) :
    global TRADE, POLONIEX, BITTREX
    _trader = POLONIEX if trader == BITTREX else BITTREX 
    if TRADE == '' or TRADE != trader :
        TRADE = trader
        _file.write("ASK_" + trader + " : " + str(ask)
                + " BID_" + BITTREX + " : " + str(bid) 
                    + ' with : ' + FORMAT.format(margin) + "\n")


def duration(_file, start) :
    end = datetime.datetime.now()
    duration = end - start
    _file.write('END AT : ' + str(end) + '\nDuring ' + str(duration) + '\n\n')

def main() :
    global TRADE, POLONIEX, BITTREX, DATE, _MARGIN
    
    period = 1 
    MARGIN = 6
    ICR = 1
    
    TIMES = 10

        # Opening File
    FILE = open("TEST1.txt","a", 1)
    FILE.write( str(DATE) + '\t For ' + str(TIMES) + ' times \n\n')
    
    while TIMES > 0 :
        ask_Poloniex , bid_Poloniex = poloniex()
        ask_Bittrex , bid_Bittrex = bittrex()
        client = Client(Keys.publicKey(), Keys.privateKey())
        tickers = client.get_orderbook_tickers()
        for i in tickers :
            if i['symbol'] == 'XLMBTC' :
                print(i['askPrice'] + " " + i['bidPrice'])
                break
        for i in range(MARGIN, MARGIN*3, ICR) :
            I = i * _MARGIN
            BUY_ON_POLONIEX = ask_Poloniex - bid_Bittrex + I
            BUY_ON_BITTREX = ask_Bittrex - bid_Poloniex + I
            
            if BUY_ON_BITTREX < 0 or BUY_ON_POLONIEX < 0 :
                print('POLONIEX : ' + FORMAT.format(BUY_ON_POLONIEX) + ' with : ' + FORMAT.format(I))
                print('BITTREX : '  + FORMAT.format(BUY_ON_BITTREX) + ' with : ' + FORMAT.format(I))
           
            if BUY_ON_POLONIEX < 0 :
                print("TRY POLONIEX")
                _buy(FILE, ask_Poloniex, bid_Bittrex, I, POLONIEX)
            elif BUY_ON_BITTREX < 0 :
                print("TRY BITTREX")
                _buy(FILE, ask_Bittrex, bid_Poloniex, I, BITTREX)

        if BUY_ON_BITTREX < 0 or BUY_ON_POLONIEX < 0 :
            FILE.write("\n")
        print("TIME : " + str(TIMES))
        TIMES -= 1
        time.sleep(period)
    
    duration(FILE, DATE)
    FILE.close()
    
if __name__ == "__main__":
    main()    
              
        
    
