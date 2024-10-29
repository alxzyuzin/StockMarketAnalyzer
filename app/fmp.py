import sys
import argparse
from stock.indicators import  ChartsData

def display_simbol_indicators(simbol:str):
    stockData = ChartsData(simbol,250)
    stockData.load()
    stockData.calcShortSMA(periodLength = 20)
    stockData.calcLongSMA(periodLength = 50)
    # Usually EMA calculates fo 12 day and 26 day period
    stockData.calcShortEMA(periodLength = 12)
    stockData.calcBollingerBand(periodlength = 20, probability =  0.95)
    stockData.calcRSI(periodLength = 20)
    stockData.calcMACD(shortPeriodLength = 12, longPeriodLength = 26, signalPeriodLength = 9)
    stockData.show(50)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--simbol", type=str)
    
    args = parser.parse_args()
    simbol = args.simbol

    display_simbol_indicators(simbol)
    
if __name__ == '__main__':
    main()

