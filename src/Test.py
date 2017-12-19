import time

from bittrex.bittrex import Bittrex, API_V1_1
from poloniex import Poloniex
from _datetime import date

if __name__ == "__main__":
    
    period = 1
    
    MARGIN = 0.00000007
    
        # Start money
    BTC_POLONIEX = 0.0023
    BTC_BITTREX = 0.0023
    XLM_POLONIEX = 0
    XLM_BITTREX = 0
    
        # Money's position
    TRADE = ''
    POLONIEX = 'POLONIEX'
    BITTREX = 'BITTREX'
    
        # Opening File
    FILE = open("TEST1.txt","a")
    
    TEST = 4000
    
    while TEST > 0:    
            # Poloniex
        polo = Poloniex()
        ticket_poloniex = polo.returnTicker()['BTC_STR']
        print(ticket_poloniex)
        ask_Poloniex = float(ticket_poloniex['lowestAsk'])      # To sell
        bid_Poloniex = float(ticket_poloniex['highestBid'])     # To buy
        
            # Bittrex
        my_bittrex = Bittrex(None, None, api_version=API_V1_1)
        ticket_bittrex = my_bittrex.get_ticker('BTC-XLM')['result']
        print(ticket_bittrex)
        ask_Bittrex = ticket_bittrex['Ask']     # To buy
        bid_Bittrex = ticket_bittrex['Bid']     # To sell
        print('{0:.8f}'.format(ask_Bittrex))
        
        
        BUY_ON_POLONIEX = ask_Poloniex - bid_Bittrex + MARGIN
        BUY_ON_BITTREX = ask_Bittrex - bid_Poloniex + MARGIN
        print('POLONIEX : ' + '{0:.8f}'.format(BUY_ON_POLONIEX))
        print('BITTREX : '  + '{0:.8f}'.format(BUY_ON_BITTREX))
           
        if BUY_ON_POLONIEX < 0 :
            print("TRY POLONIEX")
            if TRADE == '' or TRADE != POLONIEX :
                print("WRITE POLONIEX")
                TRADE = POLONIEX
                FILE.write("ASK_POLONIEX : " + str(ask_Poloniex)
                           + " BID_BITTREX : " + str(bid_Bittrex) + "\n")
        elif BUY_ON_BITTREX < 0 :
            print("TRY BITTREX")
            if TRADE == '' or TRADE != BITTREX :
                print("WRITE BITTREX")
                TRADE = BITTREX 
                FILE.write("ASK_BITTREX : " + str(ask_Bittrex)
                           + " BID_POLONIEX : " + str(bid_Poloniex) + "\n")

        print("TEST : " + str(TEST))
        TEST -= 1
        time.sleep(period)
    
    FILE.close()