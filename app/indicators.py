from datetime import datetime, timedelta
from urllib.request import urlopen
import certifi
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statistics

from app.models import IndicatorsParams
import matplotlib
matplotlib.use('Agg')

class PriceChange:
    def __init__(self, startPrice, endPrice, priceDecreasingOfset):
        self.startPrice = startPrice
        self.endPrice = endPrice
        self.priceDecreasingOfset = priceDecreasingOfset

    def __lt__(self, other):
         if (self.startPrice < other.startPrice) and (self.endPrice < other.endPrice):
            return True
         else:
             return False
        


class ChartsData:

    def __init__(self, simbol, indicators_params:IndicatorsParams ):
        # numberOfDays = 250
        # Request parameters
        self.__url = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
        self.__serietype = "line"
        self.__apikey = "VmvqJNpPV26D4SP554R2BkjnrCuJsJ2m"

        self.__simbol = simbol
        self.__history_length = indicators_params.history_length
        self.__from = (datetime.now() - timedelta(days = self.__history_length)).strftime("%Y-%m-%d")
        self.__to = datetime.now().strftime("%Y-%m-%d")
       
       # Params for calculating indicators
        self.__params = indicators_params
        
        # Source data       
        self.__date       = []
        self.__openPrice  = []
        self.__highPrice  = []
        self.__lowPrice   = []
        self.__closePrice = []
        self.__adjClose   = []
        self.__volume     = [] 
        self.__unadjustedVolume = [] 
        self.__change = []
        self.__changePercent = []
        self.__vwap = []
        self.__label = []
        self.__changeOverTime = []
        
        # Calculated indicators
        self.__first_ma    = []
        self.__second_ma     = []
        self.__third_ma     = []

        #self.__longSMALength = 0
        #self.__shortEMA   = []
        #self.__shortMALength = 0
        
        self.__RSI = []
        self.__upperBBRangeValue = []
        self.__lowerBBRangeValue = []
        #self.__BBstddevKoeff = 2

        self.__MACD = []
        self.__MACDSinalLine = []

        self.lastPrice = 0
        self.warningLevel = 0

    def load(self, history_length:int):

        self.__history_length = history_length
        self.__from = (datetime.now() - timedelta(days = history_length)).strftime("%Y-%m-%d")
        self.__to   = datetime.now().strftime("%Y-%m-%d")

        url = self.__url + self.__simbol+"?from=" + self.__from +"&to=" + self.__to + "&apikey=" + self.__apikey# + "&serietype=" + self.__serietype
        #test url with constant range for tests
        #url = 'https://financialmodelingprep.com/api/v3/historical-price-full/FSELX?from=2024-01-01&to=2024-09-07&apikey=VmvqJNpPV26D4SP554R2BkjnrCuJsJ2m'
        sourceData = []
        try:
            response = urlopen(url, cafile=certifi.where())
            data = response.read().decode("utf-8")
            sourceData = json.loads(data)
        except  Exception as msg:
            print(msg)
        
        #data_file = open("uploads\\testData.csv", "w")
       

        for datastr in reversed(sourceData["historical"]):
            self.__date.append(datetime.strptime(datastr["date"], '%Y-%m-%d').date())
            self.__openPrice.append(float(datastr["open"]))
            self.__highPrice.append(float(datastr["high"]))
            self.__lowPrice.append(float(datastr["low"]))
            self.__closePrice.append(float(datastr["close"]))
            self.__adjClose.append(float(datastr["adjClose"]))
            self.__volume.append(float(datastr["volume"]))
            self.__unadjustedVolume.append(float(datastr["unadjustedVolume"]))
            self.__change.append(float(datastr["change"]))
            self.__changePercent.append(float(datastr["changePercent"]))
            self.__vwap.append(float(datastr["vwap"]))
            self.__label.append(datastr["label"])
            self.__changeOverTime.append(float(datastr["changeOverTime"]))
            
        self.lastPrice = self.__closePrice[len(self.__closePrice) - 1]
        
    '''
        Calculate Simple Moving Average for defined range of numbers in the list
        data - list of numbers for average calculation
        periodLength - length of period for calculating average
    '''     
    def calcSMA(self, data:list, periodLength:int):
        sma = []
        for i in range(0, periodLength - 1):
            sma.append(0.0)
        for i in range(0, len(self.__date) - periodLength + 1):
            sma.append(statistics.fmean(data[i:i+periodLength]))
        return sma
   
    '''
        Calculate Exponential Moving Average for defined range of numbers in the list
        data - list of numbers for average calculation (list of close prices)
        periodLength - length of period for calculating average
    '''     
    def calcEMA(self, data:list, periodLength:int):
        multiplier = 2 / (periodLength + 1)
        ema = []
        for i in range(0, periodLength - 1):
            ema.append(0.0)
        # Calculate simple average for defined period.
        # It'll be first value for exponential average
        ema.append(statistics.fmean(data[:periodLength]))
        for i in range(periodLength, len(data)):
            ema.append(data[i] * multiplier + ema[i - 1] * (1 - multiplier))
        return ema
    
    def calcFirstMA(self, periodLength:int, matype:str):
        if matype == "sma":
            self.__first_ma = self.calcSMA(self.__closePrice, periodLength)
        if matype == "ema":
            self.__first_ma = self.calcEMA(self.__closePrice, periodLength)        

    def calcSecondMA(self, periodLength:int, matype:str):
        if matype == "sma":
            self.__second_ma = self.calcSMA(self.__closePrice, periodLength)
        if matype == "ema":
            self.__second_ma = self.calcEMA(self.__closePrice, periodLength) 
        
    def calcThirdMA(self, periodLength:int, matype:str):
        if matype == "sma":
            self.__third_ma = self.calcSMA(self.__closePrice, periodLength)
        if matype == "ema":
            self.__third_ma = self.calcEMA(self.__closePrice, periodLength) 
     
    '''
        Calculate Bollinger's band for defined period
            Band's width calculated based on probability that price lay
            inside calculated band.
            Standard calculation method calculate band width as +- 2*stddev
            from average (in this case probability = 0.95)
            data - list of numbers (dayly prices) for borders calculation
            periodlength - define period for calculation
            probability  - probability that price are inside drawed band                            price out of band
        Return 
            no return
    '''
    def calcBollingerBand(self, periodlength:int, probability:int):
        for i in range(0, periodlength):
            self.__upperBBRangeValue.append(0.0)
            self.__lowerBBRangeValue.append(0.0)
 
        for i in range(periodlength, len(self.__closePrice)):
            sample_data = self.__closePrice[i - periodlength : i]
            #sample_data = [15,15,15,15,14,17,18,21,22,24,26,29,29,30,25]
            # Calculate standard deviation
            stddev = statistics.pstdev(sample_data) 
            avr = statistics.fmean(sample_data)
           
            normDist = statistics.NormalDist(mu = avr, sigma = stddev)
            lt = (1 - probability / 100) / 2
            rt = (1 - lt)
            # Calculate border level for left tail of normal distribution plot
            lowerLimit = normDist.inv_cdf(lt)
            # Calculate border level for right tail of normal distribution plot
            upperLimit = normDist.inv_cdf(rt)
         
            self.__upperBBRangeValue.append(upperLimit)
            self.__lowerBBRangeValue.append(lowerLimit)
            
        return

    def calcRSI(self, periodLength:int):
        # Calculate Gain and Loss
        gain = [0.0]
        loss = [0.0]
        for i in range(1, len(self.__date)):
            change = self.__openPrice[i] - self.__openPrice[i-1]
            if change > 0 :
                gain.append(change)
                loss.append(0.0)
            else:
                gain.append(0)
                loss.append(0 - change)
        
        gainEMA = self.calcSMA(gain, periodLength)
        lossEMA = self.calcSMA(loss, periodLength)
        # Calculate RSI
        self.__RSI = []
        for i in range(0, periodLength):
            self.__RSI.append(0.0)
        for i in range(periodLength, len(self.__date)):
            # Приводим значение к диапазону 0 - 100
            #self.__RSI.append(100 - 100/(1 + gainEMA[i] / lossEMA[i]))
             # Приводим значение к диапазону -50 +50
            self.__RSI.append(50 - 100/(1 + gainEMA[i] / lossEMA[i]))
    
    ''' 
        Calculate Moving Average Convergence Divergence (MACD) for defined range of numbers in the list
        data - list of numbers for calculation
        periodLength - length of period for calculating MACD
    '''
    def calcMACD(self, shortPeriodLength = 12, longPeriodLength = 26, signalPeriodLength = 9):
        shortema = self.calcEMA(self.__closePrice, shortPeriodLength)
        longema = self.calcEMA(self.__closePrice, longPeriodLength)
        self.__MACD = []
        self.__MACDSinalLine = []
        for i in range(0, len(shortema)):
            self.__MACD.append(shortema[i] - longema[i])
        # Fill items in MACD list with 0.0 for items laying before meaningfull macd values
        for i in range(0, longPeriodLength - 1):
            self.__MACD[i]= 0.0
            self.__MACDSinalLine.append(0.0)
        signalLineData = self.calcEMA(self.__MACD[longPeriodLength - 1:], signalPeriodLength)
        self.__MACDSinalLine += signalLineData

    def calculate_indicators(self):
        self.calcFirstMA(self.__params.ma_first_period, self.__params.ma_first_type)
        self.calcSecondMA(self.__params.ma_second_period, self.__params.ma_second_type)
        self.calcThirdMA(self.__params.ma_third_period, self.__params.ma_third_type)
        self.calcBollingerBand(self.__params.bollingerband_period, self.__params.bollingerband_probability)
        self.calcRSI(self.__params.rsi_period)
        self.calcMACD(self.__params.macd_short_period, self.__params.macd_long_period, self.__params.macd_signal_period)
        self.calcWarningLevel()
    
    
    '''
    Build plots for all indicators
    '''
    def build_plots(self):
        startvalue = self.__params.get_offset()       
         # Define plot layout
        gs_kw = dict( height_ratios=[4, 1, 1, 1])
        fig, (ax0, ax1, ax2, ax3) = plt.subplots(4, 1,layout='constrained', gridspec_kw = gs_kw )
        #fig.tight_layout(h_pad = 0.5, w_pad = 0) # Set figure margins size
        #plt.legend(loc='upper left')
        fig.set_size_inches(14,9) 
        #fig.suptitle('Historic prices for simbol ' + self.simbol, fontsize=16)
        # Create alias for X-axe values
        x = self.__date[startvalue:]
       
        #ax0.set_title(f'Historic prices for simbol {self.__simbol} - {description} (Last price:{self.__closePrice[-1]}).')
        ax0.grid(True)
        ax0.left = 0
        # Display daily close prices and moving averages
        ax0.plot(x, self.__closePrice[startvalue:], label = "Daily prices", color='gray', linewidth = 1)
        ax0.plot(x, self.__first_ma[startvalue:],   label = "First MA")
        ax0.plot(x, self.__second_ma[startvalue:],  label = "Second MA", color = 'orange', linewidth = 1)
        ax0.plot(x, self.__third_ma[startvalue:],   label = "Third EMA", color = 'green', linewidth = 1)
        
        # Display Bellingham borders
        y1 = self.__upperBBRangeValue[startvalue:]
        y2 = self.__lowerBBRangeValue[startvalue:]
        ax0.fill_between(x, y1, y2, alpha=0.2, color='green')
        
        ax0.legend(loc='upper left')
       
        
        # format the major ticks
        #years = mdates.YearLocator()    # every year
        months = mdates.MonthLocator()  # every month
        monthsFmt = mdates.DateFormatter('%Y-%m')
        ax0.xaxis.set_major_locator(months)
        ax0.xaxis.set_major_formatter(monthsFmt)
        #
        # format the minor ticks
        days   = mdates.DayLocator(interval = 5)    # every 5 day
        daysFmt = mdates.DateFormatter('%d')
        ax0.xaxis.set_minor_locator(days)
        ax0.xaxis.set_minor_formatter(daysFmt)  # Display days numbers on x axis 

        #ax.xaxis.set_major_formatter(
        #    ConciseDateFormatter(ax.xaxis.get_major_locator()))

        ax0.tick_params(axis='x', pad=15)
        
        # Set range for displayig data
        datemin = self.__date[startvalue]
        datemax = self.__date[-1] +  timedelta(days=2) 
        ax0.set_xlim(datemin, datemax)
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        #fig.autofmt_xdate()

        #----------------------------------------------------------------------------------
        # Display volumes
        #----------------------------------------------------------------------------------
        ax1.set_title('Volumes for simbol ' + self.__simbol)
        ax1.grid(True)
        ax1.plot(self.__date[startvalue:], self.__volume[startvalue:],
                 label = "Volume", color='steelblue', linewidth = 1)
        ax1.set_xlim(datemin, datemax)
        
        #----------------------------------------------------------------------------------
        # Display RSI
        #----------------------------------------------------------------------------------
        
        ax2.set_title('RSI for simbol ' + self.__simbol)
        ax2.grid(True)
        
        ax2.plot(self.__date[startvalue:], self.__RSI[startvalue:],
                 label = "RSI", color='steelblue', linewidth = 1)
        ax2.set_xlim(datemin, datemax)
        ax2.set_ylim(-40, 40)
        # Define coords of rectangle's corners
        xcoords = [datemin, datemax, datemax, datemin]
        ycoords = [20, 20, -20, -20]
        # Draw a rectangle to display Overbought and Oversold Levels
        ax2.fill(xcoords, ycoords, alpha = 0.4, color='lightsteelblue')
        
        ax2.text(self.__date[startvalue + 10],23,"Overbought level", fontsize=10, color='gray')
        ax2.text(self.__date[startvalue + 10],-30,"Oversold level", fontsize=10, color='gray')
        ax2.legend(loc='lower left')    
        
        #----------------------------------------------------------------------------------
        # Display MACD
        #----------------------------------------------------------------------------------       
               
        ax3.set_title('MACD for simbol ' + self.__simbol)
        ax3.grid(True)
        
        ax3.plot(x, self.__MACD[startvalue:], label = "MACD", color='green', linewidth = 1)
        ax3.plot(x, self.__MACDSinalLine[startvalue:], label = "Signal line", color='blue', linewidth = 1)
        ax3.set_xlim(datemin, datemax)
        ax3.legend(loc='upper left')
        
        # Open full screen window
        mng = plt.get_current_fig_manager()
        mng.set_window_title("Indicators for simbol " + self.__simbol)
        #mng.full_screen_toggle()

        return fig
        #plt.show()
       
    def calcTrendDirection(self, number_of_days):
        events = 0
        day = 0
        
        # Look at close prices one by one and count events when 
        # price for current day less then price for previouse day
        # stop when count three such events
        # Don't take into account days when price didn't change
         
        #while events < 3:
        #    if prices[day] < prices[day + 1]:
        #        events+=1
        #    if prices[day] > prices[day + 1]:
        #        events-=1
        #    day+=1
        
        # Take prices for last days in reversed order
        prices = []
        for i in range(0,number_of_days + 1):
            prices.append(self.__closePrice[len(self.__closePrice)-i - 1])
        # Calculate price trend for peroid from prices[0] to prices[day]
        # Actually we don't need a trend line, just it's slope sign
        # in order to define positive or negative trend
        # Trend line described by equation y = ax+b
        # Pretend we have a set of points with coords x,y
        # Full formula for calculation parameters a and b in above aquation is:

        #a = ( n*S(x*y) - Sx*Sy) / n*Sx^2 - (Sx)^2
        # where:
        #  S(x*y)   - summ of multiplication x and y for each pair of coords
        #  Sx       - sum of all values of x in set
        #  Sy       - sum of all values of y in set


         # First in one cycle calculate S(x*y) 
         #  where:
         #   x - number of day
         #   y - price for that day
         #      and
         #  Sx
         #      and
         #  Sy
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_xx = 0
        days = number_of_days +1
        for x in range(0, days):
            sum_xy += prices[x]*x
            sum_x  += x
            sum_y  += prices[x]
            sum_xx += x*x

        a = ( days * sum_xy - sum_x * sum_y ) / ( days * sum_xx - sum_x * sum_x)

        return 0 - a

    def comparePriceChanging(priceChange1:PriceChange, priceChange2:PriceChange):
        if (priceChange1.startPrice < priceChange2.startPrice) and (priceChange1.endPrice < priceChange2.endPrice):
            return True

    def calcWarningLevel(self, number_of_days = 10):
        # Take prices for last days in reversed order
        WarningLevel = 0
        prices = []
        for i in range(0,number_of_days + 1):
            prices.append(self.__closePrice[len(self.__closePrice)-i - 1])

        # Put into the list last 3 price decreasing 
        listOfChangingPrice = []
        j = 0
        for i in range (0,number_of_days):
            if prices[i] < prices[i + 1]:
                listOfChangingPrice.append(PriceChange(startPrice = prices[i + 1],
                                                       endPrice=prices[i],
                                                       priceDecreasingOfset = i))
                j +=1
            if j >= 3:
                break
        if len(listOfChangingPrice) == 0:
             # Price didn'decrease last time Warning level == 0
            self.warningLevel = 0
            return 0   
        
        if len(listOfChangingPrice) == 1 and listOfChangingPrice[0].priceDecreasingOfset > 0:
            # Price price decreased in watched period but it wasn't last change
            # Actualy price went down and then went up 
            # Warning level == 0
            self.warningLevel = 0
            return 0

        if len(listOfChangingPrice) == 1 and listOfChangingPrice[0].priceDecreasingOfset == 0:
            # Price price decreased in last day of watched period
            # Warning level == 1
            self.warningLevel = 1
            return 1  

        if len(listOfChangingPrice) == 2 and listOfChangingPrice[0] < listOfChangingPrice[1]:
            # We have price decreased two times in watched period
            # and second decreasing started from lower value than first decreasing and
            # second decrising stopped on the lover value then stopped first decreasing 
            # Warning level == 2
            self.warningLevel = 2
            return 2  
        
        if (len(listOfChangingPrice) == 3 and
            listOfChangingPrice[0] < listOfChangingPrice[1] and
            listOfChangingPrice[1] < listOfChangingPrice[2]
            ):
            # We have price decreased three times in watched period
            # and each time prices decreased more
            # It means that ttrend changing from positiv to negative 
            # Warning level == 3
            self.warningLevel = 3
            return 3
        
        # No one alarming event happened so wornong level is 0
        self.warningLevel = 0
        return 0
        
