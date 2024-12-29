import numpy as np
import requests
import pandas as pd
import time
import re
import json
import xmltojson
from nsepy import get_history
from jugaad_data.nse import NSELive
from urllib.parse import unquote
from datetime import datetime, timedelta
from Constants import sleepSeconds, oneSideRelevantStrikePricesNum, defaultMaxPCRWhenZeroCallOI

baseurl = "https://scanner.tradingview.com/india/scan"

baseurlRequestHeaders = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'accept-encoding': 'deflate',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Content-Type': 'text/plain;charset=UTF-8',
    'accept': 'application/json'
}

nseLive = NSELive()

currTime = 0

startTime = datetime.now()
timeVar = startTime


def getData():
    session = requests.Session()
    body = open('resources/tradingviewScreenerQuery.json')
    response = session.post(baseurl, headers=baseurlRequestHeaders, data=body)
    print(response)
    jsonResponse = response.json()
    return jsonResponse


def fetchNSELivePrice(data):
    cnt = 0
    ibzStocks = dict()
    percentageProgress = 0
    print(f'Total NSE Stocks from TradingView is {len(data)} at {startTime}')
    percentageSet = set()

    for i in range(0, len(data)):
        percentageProgress = (i * 100) / len(data)
        percentageProgressInt = int(percentageProgress)

        if (not percentageSet.__contains__(percentageProgressInt)) and percentageProgressInt % 1 == 0:
            print(f'{percentageProgressInt}%', end=" -> ")
            percentageSet.add(percentageProgressInt)
        elif i == len(data) - 1:
            print('100% DONE')
        cnt += 1
        nsecode = str(data[i]['s']).split(":")[1]
        if ['BAJAJ_AUTO', 'NAM_INDIA'].__contains__(nsecode):
            nsecode = nsecode.replace('_', '-')
        elif nsecode.__contains__('.RR'):
            nsecode = nsecode.split('.')[0]
        elif nsecode.__contains__('_'):
            nsecode = nsecode.replace('_', '&')

        stockInfo = None
        try:
            stockInfo = nseLive.stock_quote(nsecode)['priceInfo']
        except ConnectionError as connectionError:
            print(f'nsecode={nsecode} occurred connectionError : {connectionError}')
        except Exception as exp:
            print(f'nsecode={nsecode} occurred unknown Exception : {exp}')


        if stockInfo is not None and stockInfo['open'] == stockInfo['intraDayHighLow']['min']:
            ibzStocks[nsecode] = stockInfo

    print(f'Total IBZ stocks count is {len(ibzStocks)} at {startTime}')
    print(f'IBZ stocks = {list(ibzStocks.keys())}')
    # print(ibzStocks)


def main():
    jsonResponse = getData()
    # print(f'jsonResponse : {jsonResponse}')
    data = jsonResponse['data']
    fetchNSELivePrice(data)


main()
#
# print(f'startTime={timeVar}')
# while True:
#     try:
#         main()
#     except ConnectionError as connectionError:
#         print(f'occurred connectionError : {connectionError}')
#     except Exception as exp:
#         print(f'occurred exp : {exp}')
#     timeVar = timeVar + timedelta(seconds = sleepSeconds)
#     print(f'Next Trigger-Time={timeVar}')
#     time.sleep(sleepSeconds) #in seconds
#     currTime += 1 #iterations
