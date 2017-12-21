import time

from bittrex.bittrex import Bittrex, API_V1_1
from poloniex import Poloniex
import datetime

API = API_V1_1
DATE = datetime.datetime.now()
TRADE = ''
POLONIEX = 'POLONIEX'
BITTREX = 'BITTREX'
FORMAT = '{0:.8f}'

def poloniex(market = 'BTC_STR'):
    polo = Poloniex();
    ticket_poloniex = polo.returnTicker()[market]
    print(ticket_poloniex)
    return float(ticket_poloniex['lowestAsk']) , float(ticket_poloniex['highestBid'])
    
def bittrex(market = 'BTC-XLM'):
    global API
    bittrex = Bittrex(None, None, api_version = API)
    ticket_bittrex = bittrex.get_ticker(market)['result']
    print(FORMAT.format(ticket_bittrex))
    ask_Bittrex = ticket_bittrex['Ask']
    bid_Bittrex = ticket_bittrex['Bid']
    return ask_Bittrex, bid_Bittrex

def main():
    global TRADE, POLONIEX, BITTREX, DATE
    
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
        
        
        for i in range(MARGIN, MARGIN*3, ICR) :
            I = i * 0.00000001
            BUY_ON_POLONIEX = ask_Poloniex - bid_Bittrex + i * 0.00000001
            BUY_ON_BITTREX = ask_Bittrex - bid_Poloniex + i * 0.00000001
            
            if BUY_ON_BITTREX < 0 or BUY_ON_POLONIEX < 0 :
                print('POLONIEX : ' + FORMAT.format(BUY_ON_POLONIEX) + ' with : ' + FORMAT.format(I))
                print('BITTREX : '  + FORMAT.format(BUY_ON_BITTREX) + ' with : ' + FORMAT.format(I))
           
            if BUY_ON_POLONIEX < 0 :
                print("TRY POLONIEX")
                #if TRADE == '' or TRADE != POLONIEX :
                print("WRITE POLONIEX")
                TRADE = POLONIEX
                FILE.write("ASK_POLONIEX : " + str(ask_Poloniex)
                           + " BID_BITTREX : " + str(bid_Bittrex) + ' with : ' + FORMAT.format(I) + "\n")
            elif BUY_ON_BITTREX < 0 :
                print("TRY BITTREX")
                #if TRADE == '' or TRADE != BITTREX :
                print("WRITE BITTREX")
                TRADE = BITTREX 
                FILE.write("ASK_BITTREX : " + str(ask_Bittrex)
                           + " BID_POLONIEX : " + str(bid_Poloniex) + ' with : ' + FORMAT.format(I) + "\n")

        if BUY_ON_BITTREX < 0 or BUY_ON_POLONIEX < 0 :
            FILE.write("\n")
        print("TIME : " + str(TIMES))
        TIMES -= 1
        time.sleep(period)
    
    END = datetime.datetime.now()    
    FILE.write('\nEND AT ' + str(END) + '\n\n')
    FILE.close()
    
if __name__ == "__main__":
    main()    
              
        
    
