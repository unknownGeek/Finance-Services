import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import plot
from Constants import sleepSeconds, oneSideRelevantStrikePricesNum, defaultMaxPCRWhenZeroCallOI

index = 'NIFTY'

strikePriceMinDiff = 100 if index == 'BANKNIFTY' else (50 if index == 'NIFTY' or index == 'FINNIFTY' else 0)

baseurl = "https://www.nseindia.com/"
optionChainNSEUrl = 'https://www.nseindia.com/api/option-chain-indices?symbol=' + index

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

currTime = 0
xdata = []
y1data = []
y2data = []
y3data = []
y4data = []
y5data = []
y6data = []
y7data = []
y8data = []
y9data = []
y10data = []
y11data = []
y12data = []
dynamicUpdate = plot.DynamicUpdate()
dynamicUpdate.on_launch(index)
startTime = datetime.now()
timeVar = startTime
defaultMinPCRWhenZeroPutOI = -defaultMaxPCRWhenZeroCallOI

def getData():
    session = requests.Session()
    request = session.get(baseurl, headers=headers)
    # print(request)
    cookies = dict(request.cookies)
    response = session.get(optionChainNSEUrl, headers=headers, cookies=cookies)
    # print(response)
    jsonResponse = response.json()
    print(f'jsonResponse : \n{jsonResponse}\n\n')
    rawdata = pd.DataFrame(jsonResponse)
    return rawdata


def dataFrame(rawdata):
    rawop = pd.DataFrame(rawdata['filtered']['data']).fillna(0)
    # print(rawop)
    data = []
    for i in range(0, len(rawop)):
        callOI = callCOI = callVolume = putOI = putCOI = putVolume = callLTP = 0
        strikePrice = rawop['strikePrice'][i]
        if (rawop['CE'][i] == 0):
            callOI = callCOI = callVolume = 0
        else:
            callOI = rawop['CE'][i]['openInterest']
            callCOI = rawop['CE'][i]['changeinOpenInterest']
            callLTP = rawop['CE'][i]['lastPrice']
            callVolume = rawop['CE'][i]['totalTradedVolume']

        if (rawop['PE'][i] == 0):
            putOI = putCOI = putVolume = 0
        else:
            putOI = rawop['PE'][i]['openInterest']
            putCOI = rawop['PE'][i]['changeinOpenInterest']
            putLTP = rawop['PE'][i]['lastPrice']
            putVolume = rawop['PE'][i]['totalTradedVolume']

        opdata = {
            'CALL OI': callOI, 'CALL CHNG OI': callCOI, 'CALL LTP': callLTP, 'CALL VOLUME': callVolume,
            'STRIKE PRICE': strikePrice,
            'PUT OI': putOI, 'PUT CHNG OI': putCOI, 'PUT LTP': putLTP, 'PUT VOLUME': putVolume
        }
        data.append(opdata)
    optionChain = pd.DataFrame(data)
    return optionChain


def main():
    rawData = getData()
    print(f'rawData : \n{rawData}\n\n')
    optionChain = dataFrame(rawData)

    print(f'optionChain : \n{optionChain}\n\n')

    lastModifiedAt = rawData['records'].timestamp + ' IST'
    underlyingValue = rawData['records'].underlyingValue
    callATMStrikePrice = (int)(underlyingValue / strikePriceMinDiff) * strikePriceMinDiff
    putATMStrikePrice = callATMStrikePrice + strikePriceMinDiff

    print(
        f'lastModifiedAt={lastModifiedAt} and underlyingValue={underlyingValue} and callATM={callATMStrikePrice} and putATM={putATMStrikePrice}\n')

    # print(f'optionChain:\n {optionChain}\n')

    callOptionsITM = optionChain[optionChain['STRIKE PRICE'] < callATMStrikePrice]
    callOptionsATM = optionChain[optionChain['STRIKE PRICE'] == callATMStrikePrice]
    callOptionsOTM = optionChain[optionChain['STRIKE PRICE'] > callATMStrikePrice]

    putOptionsITM = optionChain[optionChain['STRIKE PRICE'] > putATMStrikePrice]
    putOptionsATM = optionChain[optionChain['STRIKE PRICE'] == putATMStrikePrice]
    putOptionsOTM = optionChain[optionChain['STRIKE PRICE'] < putATMStrikePrice]

    # print(callOptionsITM)
    # print(callOptionsATM)
    # print(f'callOptionsOTM:\n {callOptionsOTM}\n')
    # print(f'putOptionsOTM:\n {putOptionsOTM}\n')

    # print(putOptionsITM)
    # print(putOptionsATM)
    # print(putOptionsOTM)

    callOptionsOTMSize = callOptionsOTM.size
    relevantCallOptionsOTMSize = min(callOptionsOTMSize, oneSideRelevantStrikePricesNum)
    relevantCallOptionsOTM = callOptionsOTM.iloc[0:relevantCallOptionsOTMSize]

    putOptionsOTMSize = putOptionsOTM.size
    relevantPutOptionsOTMSize = min(putOptionsOTMSize, oneSideRelevantStrikePricesNum)
    relevantPutOptionsOTM = putOptionsOTM.iloc[-relevantPutOptionsOTMSize:]

    # print(f'relevantCallOptionsOTM:\n {relevantCallOptionsOTM}\n')
    # print(f'relevantPutOptionsOTM:\n {relevantPutOptionsOTM}\n')

    relevantOptionsStrikePrices = pd.concat([relevantPutOptionsOTM, relevantCallOptionsOTM])

    print(f'relevantOptionsStrikePrices:\n {relevantOptionsStrikePrices}\n')

    resistanceLevels = pd.concat(fetchOptionWithMax(callOptionsOTM, 'CALL OI'))
    print(f'resistanceLevels :\n {resistanceLevels}\n')

    supportLevels = pd.concat(fetchOptionWithMax(putOptionsOTM, 'PUT OI'))
    print(f'supportLevels :\n {supportLevels}\n')

    resistanceLevelsStrikePrices = resistanceLevels['STRIKE PRICE'].tolist()
    print(f'resistanceLevelsStrikePrices: {resistanceLevelsStrikePrices}\n')

    supportLevelsStrikePrices = supportLevels['STRIKE PRICE'].tolist()
    print(f'supportLevelsStrikePrices: {supportLevelsStrikePrices}\n')

    totalCallIO = optionChain['CALL OI'].sum()
    totalCallCIO = optionChain['CALL CHNG OI'].sum()
    totalCallVolume = optionChain['CALL VOLUME'].sum()
    totalPutIO = optionChain['PUT OI'].sum()
    totalPutCIO = optionChain['PUT CHNG OI'].sum()
    totalPutVolume = optionChain['PUT VOLUME'].sum()

    totalRelevantCallIO = relevantOptionsStrikePrices['CALL OI'].sum()
    totalRelevantCallCIO = relevantOptionsStrikePrices['CALL CHNG OI'].sum()
    totalRelevantCallVolume = relevantOptionsStrikePrices['CALL VOLUME'].sum()
    totalRelevantPutIO = relevantOptionsStrikePrices['PUT OI'].sum()
    totalRelevantPutCIO = relevantOptionsStrikePrices['PUT CHNG OI'].sum()
    totalRelevantPutVolume = relevantOptionsStrikePrices['PUT VOLUME'].sum()

    PCR_from_total_chng_IO = calcPCR(totalPutCIO, totalCallCIO)
    PCR_from_total_IO = calcPCR(totalPutIO, totalCallIO)
    PCR_from_total_relevant_chng_IO = calcPCR(totalRelevantPutCIO, totalRelevantCallCIO)
    PCR_from_total_relevant_IO = calcPCR(totalRelevantPutIO, totalRelevantCallIO)

    # print(f'Total Call OI = {totalCallIO}, Total Call CHNG OI = {totalCallCIO}, Total Call Volume = {totalCallVolume}, Total PUT OI = {totalPutIO}, Total PUT CHNG OI = {totalPutCIO}, Total PUT Volume = {totalPutVolume}, PCR = {PCR}')

    signal_from_total_chng_IO = 'BUY' if PCR_from_total_chng_IO > 1 else 'SELL'
    signal_from_total_IO = 'BUY' if PCR_from_total_IO > 1 else 'SELL'
    signal_from_total_relevant_chng_IO = 'BUY' if PCR_from_total_relevant_chng_IO > 1 else 'SELL'


    dataPoints = {
        'Total Call OI': totalCallIO, 'Total Call CHNG OI': totalCallCIO, 'Total Call Volume': totalCallVolume,
        'Total PUT OI': totalPutIO, 'Total PUT CHNG OI': totalPutCIO, 'Total PUT Volume': totalPutVolume,
        'PCR(From Total CHNG OI)': PCR_from_total_chng_IO, 'Signal(From Total CHNG OI)': signal_from_total_chng_IO,
        'PCR(From Total OI)': PCR_from_total_IO, 'Signal(From Total OI)': signal_from_total_IO,
        'PCR(From Total Relevant CHNG OI)': PCR_from_total_relevant_chng_IO, 'Signal(From Total Relevant CHNG OI)': signal_from_total_relevant_chng_IO,
    }
    tabularDataPoints = pd.DataFrame([dataPoints])
    print(f'tabularDataPoints:\n{tabularDataPoints}\n')
    plotLines(timeVar, PCR_from_total_chng_IO, PCR_from_total_IO, totalCallIO, totalPutIO, totalCallCIO, totalPutCIO, underlyingValue, PCR_from_total_relevant_chng_IO, totalRelevantCallIO, totalRelevantPutIO, totalRelevantCallCIO, totalRelevantPutCIO)

    # plotLines(timeVar, 2 + np.sin(PCR_from_total_chng_IO*currTime), 2 + np.sin(PCR_from_total_IO*currTime), 2 + np.sin(totalCallIO*currTime), 2 + np.cos(totalPutIO*currTime), 2 + np.sin(totalCallCIO*currTime), 2 + np.cos(totalPutCIO*currTime),  2 + np.cos(underlyingValue*currTime),
    #           2 + np.sin(PCR_from_total_relevant_chng_IO*currTime), 2 + np.sin(totalRelevantCallIO*currTime), 2 + np.cos(totalRelevantPutIO*currTime), 2 + np.sin(totalRelevantCallCIO*currTime), 2 + np.cos(totalRelevantPutCIO*currTime))

    # plotLines(timeVar, 2 + np.sin(PCR_from_total_chng_IO*currTime), 2 + np.sin(PCR_from_total_IO*currTime), 2 + np.sin(totalCallIO*currTime), 2 + np.cos(totalPutIO*currTime), 2 + np.sin(totalCallCIO*currTime), 2 + np.cos(totalPutCIO*currTime),  2 + np.cos(underlyingValue*currTime))


def fetchOptionWithMax(optionsDataframe, maxColumnName):
    if optionsDataframe is None or optionsDataframe.size == 0:
        return []
    elif optionsDataframe.size == 1:
        return [optionsDataframe]
    else:
        mx = optionsDataframe[optionsDataframe[maxColumnName] == optionsDataframe[maxColumnName].max()]
        # print(f'mx : {mx}')
        if maxColumnName == 'CALL OI':
            nextMx = optionsDataframe[optionsDataframe['STRIKE PRICE'] < mx.iloc[0]['STRIKE PRICE']]
        else:
            nextMx = optionsDataframe[optionsDataframe['STRIKE PRICE'] > mx.iloc[0]['STRIKE PRICE']]
        maxOptions = fetchOptionWithMax(nextMx, maxColumnName)
        maxOptions.append(mx)
        return maxOptions

def plotLines(x, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12):
    xdata.append(x)
    y1data.append(y1)
    y2data.append(y2)
    y3data.append(y3)
    y4data.append(y4)
    y5data.append(y5)
    y6data.append(y6)
    y7data.append(y7)
    y8data.append(y8)
    y9data.append(y9)
    y10data.append(y10)
    y11data.append(y11)
    y12data.append(y12)
    # print(f'xdata={xdata} \ny1data={y1data} \ny2data={y2data} \ny3data={y3data} \ny4data={y4data} \ny5data={y5data} \ny6data={y6data} \y7data={y7data}\n')
    dynamicUpdate.on_running(xdata, y1data, y2data, y3data, y4data, y5data, y6data, y7data, y8data, y9data, y10data, y11data, y12data)

def calcPCR(putOI, callOI):
    return defaultMaxPCRWhenZeroCallOI if callOI==0 else (defaultMinPCRWhenZeroPutOI if putOI == 0 else abs(putOI / callOI))

print(f'startTime={timeVar}')
while True:
    try:
        main()
    except ConnectionError as connectionError:
        print(f'occurred connectionError : {connectionError}')
    except Exception as exp:
        print(f'occurred exp : {exp}')
    timeVar = timeVar + timedelta(seconds = sleepSeconds)
    print(f'Next Trigger-Time={timeVar}')
    time.sleep(sleepSeconds) #in seconds
    currTime += 1 #iterations
