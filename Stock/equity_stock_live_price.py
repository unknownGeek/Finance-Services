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

baseurl = "https://chartink.com/screener/"
screenerUrl = baseurl + 'process'  # https://chartink.com/screener/process

stocksFile = open('resources/stocksFile.txt', 'a')

baseurlRequestHeaders = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

screenerUrlRequestHeaders = {
    'x-xsrf-token': '-empty-',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'accept-encoding': 'deflate',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'accept': '*/*'
}

scanner_query1 = '( {cash} ( [=1] 5 minute open = [=1] 5 minute low and [=1] 5 minute open < [=1] 5 minute close and [=1] 5 minute open > 25 and [=1] 5 minute volume >= 5000 and [=1] 5 minute open > [=-1] 5 minute close * 1.01 and ( {cash} ( [=-1] 5 minute sma ( [=-1] 5 minute close , 8 ) < [=-1] 5 minute sma ( [=-1] 5 minute close , 20 ) and [=1] 5 minute sma ( [=1] 5 minute close , 20 ) < [=1] 5 minute sma ( [=1] 5 minute close , 8 ) ) ) ) ) ';

scanner_query2 = '( {cash} ( [=1] 5 minute open = [=1] 5 minute low and [=1] 5 minute open < [=1] 5 minute close and [=1] 5 minute open > 25 and [=1] 5 minute volume >= 5000 and [=1] 5 minute open > [=-1] 5 minute close * 1.001 and [=2] 5 minute low >= [=1] 5 minute low ) )'

scanner_query_ibz_vwap = '( {cash} ( monthly close > monthly upper bollinger band ( 20 , 2 ) and weekly close > weekly upper bollinger band ( 20 , 2 ) and latest close > latest upper bollinger band ( 20 , 2 ) and latest close > latest open * 1.04 and latest close > [0] 1 hour vwap and latest close > [0] 15 minute vwap and latest close > [0] 5 minute upper bollinger band ( 20 , 2 ) and latest close > [0] 5 minute vwap and market cap > 1000 and [=1] 5 minute volume > 5000 ) ) '

scanner_query_HA_LOGIC = '( {cash} ( 1 day ago open + 1 day ago close + 1 day ago low + 1 day ago high / 4 > 1 day ago open + 1 day ago close / 2 and latest volume > 250000 and latest close > 1 day ago ha-high  ) ) '

# scan_clause = scanner_query1
# scan_clause = scanner_query2
scan_clause = scanner_query_HA_LOGIC

nseLive = NSELive()

currTime = 0

startTime = datetime.now()
timeVar = startTime
defaultMinPCRWhenZeroPutOI = -defaultMaxPCRWhenZeroCallOI


def getData():
    session = requests.Session()
    request = session.get(baseurl, headers=baseurlRequestHeaders)
    # print(request)
    responseHeaders = dict(request.headers)
    responseCookies = responseHeaders['set-cookie']
    responseCookiesDict = dict(re.findall(r'([\w-]+)=([^";,]+)', responseCookies))
    xsrfToken = responseCookiesDict['XSRF-TOKEN']
    xsrfToken = unquote(xsrfToken)

    screenerUrlRequestHeaders['x-xsrf-token'] = xsrfToken

    body = {
        'scan_clause': scan_clause
    }

    screenerResponse = session.post(screenerUrl, headers=screenerUrlRequestHeaders, data=body)
    jsonResponse = screenerResponse.json()
    # print(jsonResponse)
    return jsonResponse


def fetchNSELivePrice(data):
    cnt = 0
    validStocks = []
    for i in range(0, len(data)):
        isUpperCircuit = False
        nsecode = data[i]['nsecode']
        stockInfo = getNSELivePriceInfo(nsecode)
        if stockInfo is not None:
            priceInfo = stockInfo['priceInfo']
            if priceInfo['open'] == priceInfo['upperCP']:
                isUpperCircuit = True
            else:
                validStocks.append(nsecode)
            cnt += 1
            printData(f'\n{cnt}) isUpperCircuit={isUpperCircuit} {nsecode} -> {priceInfo}')

    printData(f'\nvalidStocks={validStocks} at {startTime}')



def main():
    printData(f'\nscan_clause = {scan_clause}\n')
    jsonResponse = getData()
    printData(f'\nstartTime = {startTime}\n')
    printData(f'jsonResponse : {jsonResponse}')
    data = jsonResponse['data']
    fetchNSELivePrice(data)
    printData(f'\n\n_______________________________________________________________________________________')
    stocksFile.close()
    # getNSELivePriceInfo('BAJAJ-AUTO')

def getNSELivePriceInfo(nsecode):
    stockInfo = None
    try:
        stockInfo = nseLive.stock_quote(nsecode)
    except ConnectionError as connectionError:
        print(f'nsecode={nsecode} occurred connectionError : {connectionError}')
    except Exception as exp:
        print(f'nsecode={nsecode} occurred unknown Exception : {exp}')

    return stockInfo


def printData(str):
    stocksFile.write(str)
    print(str)

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
