#!/usr/bin/env python

#Imports
import logging
import argparse
import time
import sys

from poloniex import poloniex
from bittrex import bittrex
### END imports

try:
	# For Python 3+
	from configparser import ConfigParser, NoSectionError
except ImportError:
	# Fallback to Python 2.7
	from ConfigParser import ConfigParser, NoSectionError

# Wallets
bittrexTargetBalance = 274.69 #200$
bittrexBaseBalance = 0.0126033 #200$
bittrexTransition = 0
poloniexTargetBalance = 274.69 #200$
poloniexBaseBalance = 0.0126033 #200$
poloniexTransition = 0

## SETTERS
def setBittrexTargetBalance(newTargetBalance) :
	"""
		Set the old value bittrexTargetBalance to the new value newTargetBalance.
	"""
	global bittrexTargetBalance
	bittrexTargetBalance = newTargetBalance
	
def setBittrexBaseBalance(newBaseBalance) :
	"""
		Set the old value bittrexBaseBalance to the new value newBaseBalance.
	"""
	global bittrexBaseBalance
	bittrexBaseBalance = newBaseBalance
	
def setBittrexTransition(newTransition) :
	"""
		Set the old value bittrexTransition to the new value newTransition.
	"""
	global bittrexTransition
	bittrexTransition = newTransition
	
def setPoloniexTargetBalance(newTargetBalance) :
	"""
		Set the old value poloniexTargetBalance to the new value newTargetBalance.
	"""
	global poloniexTargetBalance
	poloniexTargetBalance = newTargetBalance
	
def setPoloniexBaseBalance(newBaseBalance) :
	"""
		Set the old value poloniexBaseBalance to the new value newBaseBalance.
	"""
	global poloniexBaseBalance
	poloniexBaseBalance = newBaseBalance
	
def setPoloniexTransition(newTransition) :
	"""
		Set the old value poloniexTransition to the new value newTransition.
	"""
	global poloniexTransition
	poloniexTransition = newTransition
### END Setters
	
	
## VARIABLES STATIQUES
# rebalance ratio
RATIO_REBALANCE = 1.03

# site name
POLO = 'Poloniex'
BIT = 'Bittrex'

TICK = 'returnTicker'
### END Variables statiques

def returnApiObjects(args, logger) :
	"""
		Return Pair Strings for accessing API responses.
	"""
	# Load Config File
	bittrexKey, bittrexSecret, poloniexKey, poloniexSecret = loadConfigFile(args, logger)
	return bittrex(bittrexKey, bittrexSecret), poloniex(poloniexKey, poloniexSecret)

def getTargetCurrency(args) :
	"""
		Return the target currency.
	"""
	return args.symbol

def getBaseCurrency(args) :
	"""
		Return the base currency.
	"""
	return args.basesymbol

def returnPair(args) :
	"""
		Return the formating currency pair. 
	"""
	# Load Configuration
	targetCurrency = getTargetCurrency(args)
	baseCurrency = getBaseCurrency(args)
	targetCurrencyPolo = 'STR' if targetCurrency == 'XLM' else targetCurrency
	return '{0}-{1}'.format(baseCurrency, targetCurrency), '{0}_{1}'.format(baseCurrency, targetCurrencyPolo)

def createLogger() :
	"""
		Initialize and return a logger.
	"""
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	return logger

def createConsoleHandler() :
	"""
		Create and return a console handler and set level to debug.
	"""
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	return ch

def createFileHandler(_logfile) :
	"""
		Create and return a file handler and set level to debug.
	"""
	fh = logging.FileHandler(_logfile, mode = 'a')
	fh.setLevel(logging.DEBUG)
	return fh

def createFormatter() :
	"""
		Create and return a formatter.
	"""
	return logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

def loadConfigFile(args, logger) :
	"""
		Load a configuration from a file, if the file don't exist
		create a configuration file.
		Return api public/secret keys. 
	"""
	config = ConfigParser()
	try:
		config.read(args.config)
		poloniexKey = config.get('ArbBot', 'poloniexKey')
		poloniexSecret = config.get('ArbBot', 'poloniexSecret')
		bittrexKey = config.get('ArbBot', 'bittrexKey')
		bittrexSecret = config.get('ArbBot', 'bittrexSecret')
		args.dryrun = True
		return bittrexKey, bittrexSecret, poloniexKey, poloniexSecret
	except NoSectionError:
		logger.warning('No Config File Found! Running in Drymode!')
		args.dryrun = True
		poloniexKey = 'POLONIEX_API_KEY'
		poloniexSecret = 'POLONIEX_API_SECRET'
		bittrexKey = 'BITTREX_API_KEY'
		bittrexSecret = 'BITTREX_API_SECRET'
		config.add_section('ArbBot')
		config.set('ArbBot', 'poloniexKey', poloniexKey)
		config.set('ArbBot', 'poloniexSecret', poloniexSecret)
		config.set('ArbBot', 'bittrexKey', bittrexKey)
		config.set('ArbBot', 'bittrexSecret', bittrexSecret)
		try:
			with open(args.config, 'w') as configfile:
				config.write(configfile)
		except IOError:
			logger.error('Failed to create and/or write to {}'.format(args.config))
		return bittrexKey, bittrexSecret, poloniexKey, poloniexSecret
	
def quit(_logger) :
	"""
		Exit the program with a information message.
	"""
	_logger.info('KeyboardInterrupt, quitting!')
	sys.exit()

def writeError(logger, _buyExchange, trade, _pair) :
	logger.error('Failed to get {} {}s for {}, skipping order attempt'.format(_buyExchange, trade, _pair))


def setupArgs() :
	"""
		Setup Argument Parser.
		Return the arguments.
	"""
	parser = argparse.ArgumentParser(description='Poloniex/Bittrex Arbitrage Bot')
	parser.add_argument('-s', '--symbol', default='SC', type=str, required=False, help='symbol of your target coin [default: XMR]')
	parser.add_argument('-b', '--basesymbol', default='BTC', type=str, required=False, help='symbol of your base coin [default: BTC]')
	parser.add_argument('-r', '--rate', default=1.004, type=float, required=False, help='minimum price difference, 1.01 is 1 percent price difference (exchanges charge .05 percent fee) [default: 1.01]')
	parser.add_argument('-m', '--max', default=0.0, type=float, required=False, help='maximum order size in target currency (0.0 is unlimited) [default: 0.0]')
	parser.add_argument('-i', '--interval', default=1, type=int, required=False, help='seconds to sleep between loops [default: 1]')
	parser.add_argument('-c', '--config', default='arbbot.conf', type=str, required=False, help='config file [default: arbbot.conf]')
	parser.add_argument('-l', '--logfile', default='arbbot.log', type=str, required=False, help='file to output log data to [default: arbbot.log]')
	parser.add_argument('-d', '--dryrun', action='store_true', required=False, help='simulates without trading (API keys not required)')
	parser.add_argument('-v', '--verbose', action='store_true', required=False, help='enables extra console messages (for debugging)')
	return parser.parse_args()

def main(argv):

	global _buyExchange
	args = setupArgs()

	bittrexPair, poloniexPair = returnPair(args)

	logger = createLogger()
	ch = createConsoleHandler()
	fh = createFileHandler(args.logfile)
	formatter = createFormatter()
	
	# Add formatter to handlers
	ch.setFormatter(formatter)
	fh.setFormatter(formatter)

	# Add handlers to logger
	logger.addHandler
	logger.addHandler(fh)

	# Log Startup Settings
	logger.info('Arb Pair: {} | Rate: {} | Interval: {} | Max Order Size: {}'.format(bittrexPair, args.rate, args.interval, args.max))
	if args.dryrun:
		logger.info("Dryrun Mode Enabled (will not trade)")

	bittrexAPI,	poloniexAPI = returnApiObjects(args, logger)



	def reBalance(_buyExchange, tradesize, arbitrage):
	
		def exchange(_buyExchange = _buyExchange) :
			"""
				Return the "opposite" of _buyExchange.
			"""
			return POLO if _buyExchange != POLO else BIT
		### END exchange()		
		Acurrency = 'XRP'

		def setTradesize(newTradesize) :
			global tradesize
			tradesize = newTradesize
		### END setTradeSize()			
			
		
		def currencyPair(currency, sender = BIT) :
			return "{}-{}".format(getBaseCurrency(args), currency) if sender == BIT else "{}_{}".format(getBaseCurrency(args), currency)
		### END currencyPair()
		
		def transferInfo(currency, targetBalance, sender) :
			_exchange = exchange(sender)
			logger.critical("Transfert de {} {} de {} vers {} avec {} {}".format(tradesize, currency, sender, _exchange, targetBalance, currency))
		### END transferInfo
		
		def tradeInfo(currency, trade, sender) :
			_exchange = exchange(sender)
			trade = "Vente" if trade == "sell" else "Achat"
			logger.critical("{} de {} à {} {} sur {}".format(trade, currency, tradesize, getBaseCurrency(args), _exchange))
		### END tradeInfo()
		
		def transferTarget() :
			currency = getTargetCurrency(args)
			if _buyExchange == POLO :
				tradesize = poloniexTargetBalance
				setBittrexTargetBalance(bittrexBaseBalance + tradesize)
				setPoloniexTargetBalance(0)
				time.sleep(5) # duree de l'envoi d'un portefeuille à un autre
				transferInfo(currency, bittrexTargetBalance, POLO)
			if _buyExchange == BIT :
				tradesize = bittrexTargetBalance
				setPoloniexTargetBalance(poloniexTargetBalance + tradesize)
				setBittrexTargetBalance(0)
				time.sleep(5) # duree de l'envoi d'un portefeuille à un autre
				transferInfo(currency, poloniexTargetBalance, BIT)
		### END transferTarget()
		
		def sellTarget() :
			currency = getTargetCurrency(args)
			if _buyExchange == POLO :
				summary = bittrexAPI.getmarketsummary(bittrexPair)
				setBittrexTargetBalance(bittrexTargetBalance - tradesize) # tradesize in target currency
				setTradesize(tradesize * summary[0]['Ask']) # tradesize in base currency
				setBittrexBaseBalance(bittrexBaseBalance + tradesize)
				tradeInfo(currency, 'sell', BIT)
			if _buyExchange == BIT :
				summary = poloniexAPI.api_query(TICK) 
				setPoloniexTargetBalance(poloniexTargetBalance - tradesize)
				setTradesize(tradesize * summary[poloniexPair]["lowestAsk"])
				setPoloniexBaseBalance(poloniexBaseBalance + tradesize)
				tradeInfo(currency, 'sell', POLO)
		### END sellTarget()
		
		def buyACurrency(currency) :
			if _buyExchange == POLO :
				_currencyPair = currencyPair(currency)
				print("CURRENCY : {}".format(_currencyPair))
				summary = bittrexAPI.getmarketsummary(_currencyPair)
				setBittrexBaseBalance(bittrexBaseBalance - tradesize) # tradesize in currency
				print("Summary : {} ".format(summary))
				setTradesize(tradesize / summary[0]['Ask'])
				tradeInfo(currency, 'buy', BIT)
			if _buyExchange == BIT :
				_currencyPair = currencyPair(currency, POLO)
				summary = poloniexAPI.api_query(TICK)
				setPoloniexBaseBalance(poloniexBaseBalance - tradesize)
				setTradesize(tradesize / summary[_currencyPair]["lowestAsk"])
				tradeInfo(currency, 'buy', POLO)
		### END buyACurrency()
		
		def sendACurrency(currency) :
			transferInfo(currency, poloniexTransition, POLO)
			setBittrexTransition(bittrexTransition - tradesize)
			setPoloniexTransition(poloniexTransition + tradesize)
			time.sleep(5)
		### END sendACurrency()
		
		def sellACurrency(currency) :
			if _buyExchange == POLO :
				_currencyPair = currencyPair(currency, POLO)
				summary = poloniexAPI.api_query(TICK)
				sellCurrencyToBase = float(summary[_currencyPair]["lowestAsk"]) * poloniexTransition
				setPoloniexBaseBalance(poloniexBaseBalance + sellCurrencyToBase)
				setPoloniexTransition(0)
				setTradesize(0)
				return sellCurrencyToBase
		### END sellACurrency()
		
		def buyBaseWithCurrency(amount, currency) :
			if _buyExchange == POLO :
				_currencyPair = currencyPair(currency, POLO)
				summary = poloniexAPI.api_query(TICK)
				setPoloniexTargetBalance(poloniexTargetBalance + amount / float(summary[_currencyPair]["lowestAsk"]))
				tradeInfo(currency, 'sell', POLO)
				setPoloniexBaseBalance(poloniexBaseBalance - amount)
		### END buyBaseWithCurrency()
			
		# pas assez de btc pour acheter du xlm dans poloniex/bittrex
		if arbitrage > RATIO_REBALANCE :
			
			# transfert XLM polo vers XLM poloniex/bittrex
			transferTarget()
			
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
			buyBaseWithCurrency(amountCurrency, Acurrency)
			
			
			logger.info("\nNouveau : \nBittrex BTC  {} | Bittrex LUMEN: {}\nPoloniex BTC: {} | Poloniex LUMEN {}".format(bittrexBaseBalance, bittrexTargetBalance, poloniexBaseBalance, poloniexTargetBalance))
	### END reBalance()

	"""
Notre statégie suppose que le prix du XLM est plus bas sur Poloniex que sur Bittrex
est que la différence de prix entre le BTC et XRP des 2 plateformes est très faible
	"""
# trade simulation function
	def tradeSimulation(_buyExchange, _ask, _bid, _sellBalance, _buyBalance):
		def exchange(_buyExchange = _buyExchange) :
			"""
				Return the "opposite" of _buyExchange.
			"""
			return POLO if _buyExchange != POLO else BIT
		### END exchange()
		arbitrage = _bid/_ask
		print('DEBUG: Current Rate: {} | Minimum Rate: {}'.format(arbitrage, args.rate))
		
		def bitBook(trade) :
			return bittrexAPI.getorderbook(bittrexPair, trade)[0]["Quantity"]
		### END bitBook()
		
		def poloBook(trade) :
			return poloniexAPI.returnOrderBook(poloniexPair)[trade][0][1]
		### END bitBook()
		
		def sellBook() :
			if _buyExchange == POLO :
				try :
					return poloBook('Aks')
				except KeyboardInterrupt :
					quit(logger)
				except :
					writeError(logger, POLO, 'Ask', poloniexPair)
					return None
			if _buyExchange == BIT :
				try :
					return  bitBook('sell')
				except KeyboardInterrupt :
					quit(logger)
				except :
					writeError(BIT, 'Bid', bittrexPair)
					return None
		### END sellBook()
		
		def buyBook() :
			if _buyExchange == POLO :
				try :
					return bitBook('buy')
				except KeyboardInterrupt :
					quit(logger)
				except :
					writeError(BIT, 'Ask', bittrexPair)
					return None
			if _buyExchange == BIT :
				try :
					return poloBook('bids')
				except KeyboardInterrupt :
					quit(logger)
				except :
					writeError(POLO, 'Bid', poloniexPair)
					return None
		### END buyBook()
		
		# Return if minumum arbitrage percentage is not met
		if arbitrage <= args.rate:
			return
		_sellExchange = exchange()
		sellbook = sellBook()
		buybook = buyBook()
		sellbook = 0 if sellbook == None else sellbook
		buybook = 0 if buybook == None else buybook
		
		
		logger.info('OPPORTUNITY: BUY @ ' + _buyExchange + ' | SELL @ ' + _sellExchange + ' | RATE: ' + str(arbitrage) + '%')

		#Find minimum order size
		tradesize = min(sellbook, buybook)

		#Setting order size incase balance not enough
		if _sellBalance < tradesize:
			logger.info('Tradesize ({}) larger than sell balance ({} @ {}), lowering tradesize.'.format(tradesize, _sellBalance, _sellExchange))
			tradesize = _sellBalance

		if (tradesize*_ask) > _buyBalance:
			newTradesize = _buyBalance / _ask
			logger.info('Tradesize ({}) larger than buy balance ({} @ {}), lowering tradesize to {}.'.format(tradesize, _buyBalance, _buyExchange, newTradesize))
			tradesize = newTradesize


		#Check if above min order size
		#Fonctionnement normal du bot il achete et vend en binaire (arbitrage)
		if (tradesize*_bid) > 0.0006001: # less than 10$
 
			logger.info("ORDER {}\nSELL: {}	| {} @ {:.8f} (Balance: {})\nBUY: {}	| {} @ {:.8f} (Balance: {})".format(bittrexPair, _sellExchange, tradesize, _bid, _sellBalance, _buyExchange, tradesize, _ask, _buyBalance))



			#Execute order
			# Wallet simulation
			if _buyExchange == POLO:
				#Sell on Bittrex 
				setBittrexTargetBalance (bittrexTargetBalance - tradesize)
				setBittrexBaseBalance(bittrexBaseBalance + (tradesize * _bid))
				#Buy on Poloniex
				setPoloniexBaseBalance(poloniexBaseBalance - (tradesize * _ask))
				setPoloniexTargetBalance(poloniexTargetBalance + tradesize)
			elif _buyExchange == BIT:
				#Buy on Bittrex 
				setBittrexTargetBalance(bittrexTargetBalance + tradesize)
				setBittrexBaseBalance(bittrexBaseBalance - (tradesize * _ask))
				#Sell on Poloniex
				setPoloniexBaseBalance(poloniexBaseBalance + (tradesize * _bid))
				setPoloniexTargetBalance(poloniexTargetBalance - tradesize)

			logger.info("\nBittrex BTC  {} | Bittrex LUMEN: {}\nPoloniex BTC: {} | Poloniex LUMEN {}".format(bittrexBaseBalance, bittrexTargetBalance, poloniexBaseBalance, poloniexTargetBalance, _sellBalance))
			logger.info("Dryrun: skipping order")
			
			# pas assez pour acheter du XLM 
		else:
			reBalance(_buyExchange, tradesize, arbitrage)
			logger.warning("Order size not above min order size, no trade was executed")



	i = 1
	# Main Loop
	while True:
		if i == 50:
			break;
		i += 1
		print("=================DEBUT=====================")
		# Query Poloniex Prices
		try:
			currentValues = poloniexAPI.api_query(TICK)
			print(currentValues[poloniexPair])
		except KeyboardInterrupt:
			quit(logger)
		except:
			logger.error('Failed to Query Poloniex API, Restarting Loop')
			continue
		poloBid = float(currentValues[poloniexPair]["highestBid"])
		poloAsk = float(currentValues[poloniexPair]["lowestAsk"])
		
		# Query Bittrex Prices
    
		try:
			summary=bittrexAPI.getmarketsummary(bittrexPair)
			print(summary)
            
		except KeyboardInterrupt:
			quit(logger)
		
		except:
			logger.error('Failed to Query Bittrex API, Restarting Loop')
			continue
		
		bittrexAsk = summary[0]['Ask']
		bittrexBid = summary[0]['Bid']

		# Buy from Polo, Sell to Bittrex
		if poloAsk < bittrexBid:
			print("Polo achat ?")
			tradeSimulation(POLO, poloAsk, bittrexBid, bittrexTargetBalance, poloniexBaseBalance)
		# Sell to polo, Buy from Bittrex
		if bittrexAsk < poloBid:
			print("Polo vente ?")
			tradeSimulation(BIT, bittrexAsk, poloBid, poloniexTargetBalance, bittrexBaseBalance)

		time.sleep(args.interval)


if __name__ == "__main__":
	main(sys.argv[1:])
