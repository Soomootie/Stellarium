#!/usr/bin/env python
#Imports
import logging
import argparse
import time
import sys

from poloniex import poloniex
from bittrex import bittrex
try:
	# For Python 3+
	from configparser import ConfigParser, NoSectionError
except ImportError:
	# Fallback to Python 2.7
	from ConfigParser import ConfigParser, NoSectionError

# wallet
bittrexTargetBalance=274.69 #200$
bittrexBaseBalance=0.0126033 #200$
bittrexTransition = 0
poloniexTargetBalance=274.69 #200$
poloniexBaseBalance=0.0126033 #200$
poloniexTransition = 0

# rebalance ratio
RATIO_REBALANCE = 1.03


def main(argv):
	"""
	#simulation balance
	bittrexTargetBalance=274.69 #200$
	bittrexBaseBalance=0.0126033 #200$
	poloniexTargetBalance=274.69 #200$
	poloniexBaseBalance=0.0126033 #200$
	"""
	global bittrexTargetBalance
	global bittrexBaseBalance
	global bittrexTransition
	global poloniexTargetBalance
	global poloniexBaseBalance
	global poloniexTransition

	# Setup Argument Parser
	parser = argparse.ArgumentParser(description='Poloniex/Bittrex Arbitrage Bot')
	parser.add_argument('-s', '--symbol', default='XLM', type=str, required=False, help='symbol of your target coin [default: XMR]')
	parser.add_argument('-b', '--basesymbol', default='BTC', type=str, required=False, help='symbol of your base coin [default: BTC]')
	parser.add_argument('-r', '--rate', default=1.004, type=float, required=False, help='minimum price difference, 1.01 is 1 percent price difference (exchanges charge .05 percent fee) [default: 1.01]')
	parser.add_argument('-m', '--max', default=0.0, type=float, required=False, help='maximum order size in target currency (0.0 is unlimited) [default: 0.0]')
	parser.add_argument('-i', '--interval', default=1, type=int, required=False, help='seconds to sleep between loops [default: 1]')
	parser.add_argument('-c', '--config', default='arbbot.conf', type=str, required=False, help='config file [default: arbbot.conf]')
	parser.add_argument('-l', '--logfile', default='arbbot.log', type=str, required=False, help='file to output log data to [default: arbbot.log]')
	parser.add_argument('-d', '--dryrun', action='store_true', required=False, help='simulates without trading (API keys not required)')
	parser.add_argument('-v', '--verbose', action='store_true', required=False, help='enables extra console messages (for debugging)')
	args = parser.parse_args()

	# Load Configuration
	targetCurrency = args.symbol
	baseCurrency = args.basesymbol
	
	if args.symbol == 'XLM':
		targetCurrencyPolo = 'STR'
	else:
		targetCurrencyPolo = args.symbol
		
	# Pair Strings for accessing API responses
	bittrexPair = '{0}-{1}'.format(baseCurrency, targetCurrency)
	poloniexPair = '{0}_{1}'.format(baseCurrency, targetCurrencyPolo)
	poloXRPair = '{0}_{1}'.format(baseCurrency, 'XRP')
	bitXRPair = '{0}_{1}'.format(baseCurrency, 'XRP')

	# Create Logger
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	# Create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	# Create file handler and set level to debug
	fh = logging.FileHandler(args.logfile, mode='a', encoding=None, delay=False)
	fh.setLevel(logging.DEBUG)
	# Create formatter
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	# Add formatter to handlers
	ch.setFormatter(formatter)
	fh.setFormatter(formatter)

	# Add handlers to logger
	logger.addHandler(ch)
	logger.addHandler(fh)

	# Load Config File
	config = ConfigParser()
	try:
		config.read(args.config)
		poloniexKey = config.get('ArbBot', 'poloniexKey')
		poloniexSecret = config.get('ArbBot', 'poloniexSecret')
		bittrexKey = config.get('ArbBot', 'bittrexKey')
		bittrexSecret = config.get('ArbBot', 'bittrexSecret')
		args.dryrun = True
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

	# Log Startup Settings
	logger.info('Arb Pair: {} | Rate: {} | Interval: {} | Max Order Size: {}'.format(bittrexPair, args.rate, args.interval, args.max))
	if args.dryrun:
		logger.info("Dryrun Mode Enabled (will not trade)")

	# Create Exchange API Objects
	bittrexAPI = bittrex(bittrexKey, bittrexSecret)
	poloniexAPI = poloniex(poloniexKey, poloniexSecret)
	def quit():
		logger.info('KeyboardInterrupt, quitting!')
		sys.exit()



	def reBalance(_buyExchange, tradesize, arbitrage):
		
		global bittrexTargetBalance #XLM 200$
		global bittrexBaseBalance #BTC 200$
		global poloniexTargetBalance #XLM 200$
		global poloniexBaseBalance #BTC 200$
		global bittrexTransition #XRP 200$
		global poloniexTransition #XRP 200$
		

					# pas assez pour acheter du xlm dans poloniex
		if _buyExchange == 0 and arbitrage > RATIO_REBALANCE :
			
			# transfert XLM polo vers XLM bittrex
			tradesize = poloniexTargetBalance
			bittrexTargetBalance += tradesize
			poloniexTargetBalance = 0
			time.sleep(5) # duree de l'envoi d'un portefeuille à un autre
			logger.warning("Transfert de {} XLM de Poloniex vers Bittrex avec {} XLM".format(tradesize, bittrexTargetBalance))
			
			# vend le XLM sur bittrex
			summary=bittrexAPI.getmarketsummary(bittrexPair)
			bittrexTargetBalance -= tradesize #tradesize in XLM
			tradesize = tradesize * summary[0]['Ask'] #Tradesize in BTC
			bittrexBaseBalance += tradesize
			logger.warning("Vente de XLM à {} BTC sur Bittrex".format(tradesize))
			
			# !! verif le tradesize de xrp aussi
			# achete XRP bittrex avec BTC 
			summary = bittrexAPI.getmarketsummary('BTC-XRP')
			bittrexBaseBalance -= tradesize
			tradesize = tradesize / summary[0]['Ask']
			bittrexTransition += tradesize #tradesize in XRP
			logger.warning("Achat de {} XRP sur Bittrex ".format(tradesize))
			
			# XRP bittrex envoi vers XRP polo
			time.sleep(0.5)
			logger.warning("Transfert de {} XRP de Bittrex vers Poloniex avec {} XRP".format(tradesize, poloniexTransition))
			bittrexTransition -= tradesize
			poloniexTransition += tradesize
			
			# convert XRP polo en BTC
			currentValues = poloniexAPI.api_query("returnTicker")
			sell_XRP_to_BTC = float(currentValues['BTC_XRP']["lowestAsk"]) * poloniexTransition
			poloniexBaseBalance += sell_XRP_to_BTC
			poloniexTransition = 0
			tradesize = 0
			
			# buy XLM with BTC on Poloniex
			poloniexTargetBalance += sell_XRP_to_BTC / float(currentValues['BTC_SC']["lowestAsk"])
			logger.warning("Achat de {} XLM sur Poloniex avec {} BTC".format(poloniexTargetBalance, sell_XRP_to_BTC))
			poloniexBaseBalance -= sell_XRP_to_BTC
			
			
			logger.info("\nNouveau : \nBittrex BTC  {} | Bittrex LUMEN: {}\nPoloniex BTC: {} | Poloniex LUMEN {}".format(bittrexBaseBalance, bittrexTargetBalance, poloniexBaseBalance, poloniexTargetBalance, _sellBalance))

				
				

	"""
Notre statégie suppose que le prix du XLM est plus bas sur Poloniex que sur Bittrex
est que la différence de prix entre le BTC et XRP des 2 plateformes est très faible
	"""
# trade simulation function
	def tradeSimulation(_buyExchange, _ask, _bid, _sellBalance, _buyBalance):
		#simulation balance
		global bittrexTargetBalance #XLM 200$
		global bittrexBaseBalance #BTC 200$
		global poloniexTargetBalance #XLM 200$
		global poloniexBaseBalance #BTC 200$
		global bittrexTransition #XRP 200$
		global poloniexTransition #XRP 200$
		# _buyExchange:
		# 0 = Poloniex
		# 1 = Bittrex
		arbitrage = _bid/_ask
		# Return if minumum arbitrage percentage is not met
		print('DEBUG: Current Rate: {} | Minimum Rate: {}'.format(arbitrage, args.rate))
		if arbitrage <= args.rate:
			return
		elif _buyExchange == 0:
			buyExchangeString = 'Poloniex'
			sellExchangeString = 'Bittrex'

			# Load Sellbook from Poloniex, Fail Gracefully
			try:
				sellbook = poloniexAPI.returnOrderBook(poloniexPair)["asks"][0][1]
			except KeyboardInterrupt:
				quit()
			except:
				logger.error('Failed to get Poloniex Asks for {}, skipping order attempt'.format(poloniexPair))
				return

			# Load Buybook from Bittrex, Fail Gracefully
			try:
				buybook = bittrexAPI.getorderbook(bittrexPair, "buy")[0]["Quantity"]
			except KeyboardInterrupt:
				quit()
			except:
				logger.error('Failed to get Bittrex Asks for {}, skipping order attempt'.format(poloniexPair))
				return
		elif _buyExchange == 1:
			buyExchangeString = 'Bittrex'
			sellExchangeString = 'Poloniex'

			# Load Buybook from Poloniex, Fail Gracefully
			try:
				buybook = poloniexAPI.returnOrderBook(poloniexPair)["bids"][0][1]
			except KeyboardInterrupt:
				quit()
			except:
				logger.error('Failed to get Bittrex Bids for {}, skipping order attempt'.format(poloniexPair))
				return

			# Load Sellbook from Bittrex, Fail Gracefully
			try:
				sellbook = bittrexAPI.getorderbook(bittrexPair, "sell")[0]["Quantity"]
			except KeyboardInterrupt:
				quit()
			except:
				logger.error('Failed to get Bittrex Asks for {}, skipping order attempt'.format(poloniexPair))
				return

		logger.info('OPPORTUNITY: BUY @ ' + buyExchangeString + ' | SELL @ ' + sellExchangeString + ' | RATE: ' + str(arbitrage) + '%')

		#Find minimum order size
		tradesize = min(sellbook, buybook)

		#Setting order size incase balance not enough
		if _sellBalance < tradesize:
			logger.info('Tradesize ({}) larger than sell balance ({} @ {}), lowering tradesize.'.format(tradesize, _sellBalance, sellExchangeString))
			tradesize = _sellBalance

		if (tradesize*_ask) > _buyBalance:
			newTradesize = _buyBalance / _ask
			logger.info('Tradesize ({}) larger than buy balance ({} @ {}), lowering tradesize to {}.'.format(tradesize, _buyBalance, buyExchangeString, newTradesize))
			tradesize = newTradesize


		#Check if above min order size
		#Fonctionnement normal du bot il achete et vend en binaire (arbitrage)
		if (tradesize*_bid) > 0.0006001: # less than 10$
 
			logger.info("ORDER {}\nSELL: {}	| {} @ {:.8f} (Balance: {})\nBUY: {}	| {} @ {:.8f} (Balance: {})".format(bittrexPair, sellExchangeString, tradesize, _bid, _sellBalance, buyExchangeString, tradesize, _ask, _buyBalance))



			#Execute order
			# Wallet simulation
			if _buyExchange == 0:
				#Sell on Bittrex 
				bittrexTargetBalance = bittrexTargetBalance - tradesize
				bittrexBaseBalance = bittrexBaseBalance + (tradesize * _bid)
				#Buy on Poloniex
				poloniexBaseBalance = poloniexBaseBalance - (tradesize * _ask)
				poloniexTargetBalance = poloniexTargetBalance + tradesize
			elif _buyExchange == 1:
				#Buy on Bittrex 
				bittrexTargetBalance = bittrexTargetBalance + tradesize
				bittrexBaseBalance = bittrexBaseBalance - (tradesize * _ask)
				#Sell on Poloniex
				poloniexBaseBalance = poloniexBaseBalance + (tradesize * _bid)
				poloniexTargetBalance = poloniexTargetBalance - tradesize

			logger.info("\nBittrex BTC  {} | Bittrex LUMEN: {}\nPoloniex BTC: {} | Poloniex LUMEN {}".format(bittrexBaseBalance, bittrexTargetBalance, poloniexBaseBalance, poloniexTargetBalance, _sellBalance))
			logger.info("Dryrun: skipping order")
			
			# pas assez pour acheter du XLM 
		else:
			reBalance(_buyExchange, tradesize, arbitrage)
			logger.warning("Order size not above min order size, no trade was executed")




	# Main Loop
	while True:
		print("=================DEBUT=====================")
		# Query Poloniex Prices
		#print (bittrexPair)
		#bittrexPair = 'btc-ltc'
		try:
			currentValues = poloniexAPI.api_query("returnTicker")
		except KeyboardInterrupt:
			quit()
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
			quit()
		
		except:
			logger.error('Failed to Query Bittrex API, Restarting Loop')
			continue
		
		bittrexAsk = summary[0]['Ask']
		bittrexBid = summary[0]['Bid']



	else:

		# Buy from Polo, Sell to Bittrex
		if poloAsk < bittrexBid:
			print("Polo achat ?")
			tradeSimulation(0, poloAsk, bittrexBid, bittrexTargetBalance, poloniexBaseBalance)
		# Sell to polo, Buy from Bittrex
		if bittrexAsk < poloBid:
			print("Polo vente ?")
			tradeSimulation(1, bittrexAsk, poloBid, poloniexTargetBalance, bittrexBaseBalance)

		time.sleep(args.interval)


if __name__ == "__main__":
	main(sys.argv[1:])
