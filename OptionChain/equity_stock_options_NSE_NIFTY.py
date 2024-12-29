import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from Constants import sleepSeconds, defaultMaxPCRWhenZeroCallOI

index = 'NIFTY 50'

strikePriceMinDiff = 100 if index == 'BANKNIFTY' else (50 if index == 'NIFTY' or index == 'FINNIFTY' else 0)

baseurl = "https://www.nseindia.com/"
optionChainNSEUrl = 'https://www.nseindia.com/api/equity-stockIndices?index=' + index

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
# dynamicUpdate = plot.DynamicUpdate()
# dynamicUpdate.on_launch(index)
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
    # print(jsonResponse)
    # rawdata = pd.DataFrame(jsonResponse)
    rawdata = jsonResponse
    return rawdata



def dataFrame(rawdata):
    rawop = pd.DataFrame(rawdata['data']).fillna(0)
    # print(f'rawop : {rawop}')
    lastModifiedTs = rawdata['timestamp'] + ' IST'
    print(f'lastModifiedTs : {lastModifiedTs}')

    data = []
    for i in range(0, len(rawop)):
        change = pChange = 0
        symbol = rawop['symbol'][i]
        # companyName = rawop['meta'][i]
        lastPrice = rawop['lastPrice'][i]
        if rawop['change'][i] == 0:
            change = pChange = 0
        else:
            change = rawop['change'][i]
            pChange = rawop['pChange'][i]
            pChange100 = pChange*100

        opdata = {
            'symbol': symbol, 'lastPrice': lastPrice, 'change': change, 'pChange': pChange, 'pChange100': pChange100
        }
        data.append(opdata)
    pChanges = pd.DataFrame(data)
    return pChanges


def main():
    rawData = getData()
    # print(f'rawData : {rawData}')
    pChanges = dataFrame(rawData)
    print(f'pChanges Table:\n{pChanges}\n')

    # print(
    #     f'lastModifiedAt={lastModifiedAt} and underlyingValue={underlyingValue} and callATM={callATMStrikePrice} and putATM={putATMStrikePrice}\n')

    # print(f'optionChain:\n {optionChain}\n')

    # print(f'Total Call OI = {totalCallIO}, Total Call CHNG OI = {totalCallCIO}, Total Call Volume = {totalCallVolume}, Total PUT OI = {totalPutIO}, Total PUT CHNG OI = {totalPutCIO}, Total PUT Volume = {totalPutVolume}, PCR = {PCR}')

    # dataPoints = {
    #     'Total Call OI': totalCallIO, 'Total Call CHNG OI': totalCallCIO, 'Total Call Volume': totalCallVolume,
    #     'Total PUT OI': totalPutIO, 'Total PUT CHNG OI': totalPutCIO, 'Total PUT Volume': totalPutVolume,
    #     'PCR(From Total CHNG OI)': PCR_from_total_chng_IO, 'Signal(From Total CHNG OI)': signal_from_total_chng_IO,
    #     'PCR(From Total OI)': PCR_from_total_IO, 'Signal(From Total OI)': signal_from_total_IO,
    #     'PCR(From Total Relevant CHNG OI)': PCR_from_total_relevant_chng_IO, 'Signal(From Total Relevant CHNG OI)': signal_from_total_relevant_chng_IO,
    # }
    # tabularDataPoints = pd.DataFrame([dataPoints])
    # print(f'tabularDataPoints:\n{tabularDataPoints}\n')

    # plotLines(timeVar, PCR_from_total_chng_IO, PCR_from_total_IO, totalCallIO, totalPutIO, totalCallCIO, totalPutCIO, underlyingValue, PCR_from_total_relevant_chng_IO, totalRelevantCallIO, totalRelevantPutIO, totalRelevantCallCIO, totalRelevantPutCIO)

    # plotLines(timeVar, 2 + np.sin(PCR_from_total_chng_IO*currTime), 2 + np.sin(PCR_from_total_IO*currTime), 2 + np.sin(totalCallIO*currTime), 2 + np.cos(totalPutIO*currTime), 2 + np.sin(totalCallCIO*currTime), 2 + np.cos(totalPutCIO*currTime),  2 + np.cos(underlyingValue*currTime),
    #           2 + np.sin(PCR_from_total_relevant_chng_IO*currTime), 2 + np.sin(totalRelevantCallIO*currTime), 2 + np.cos(totalRelevantPutIO*currTime), 2 + np.sin(totalRelevantCallCIO*currTime), 2 + np.cos(totalRelevantPutCIO*currTime))

    # plotLines(timeVar, 2 + np.sin(PCR_from_total_chng_IO*currTime), 2 + np.sin(PCR_from_total_IO*currTime), 2 + np.sin(totalCallIO*currTime), 2 + np.cos(totalPutIO*currTime), 2 + np.sin(totalCallCIO*currTime), 2 + np.cos(totalPutCIO*currTime),  2 + np.cos(underlyingValue*currTime))


# def plotLines(x, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12):
#     xdata.append(x)
#     y1data.append(y1)
#     y2data.append(y2)
#     y3data.append(y3)
#     y4data.append(y4)
#     y5data.append(y5)
#     y6data.append(y6)
#     y7data.append(y7)
#     y8data.append(y8)
#     y9data.append(y9)
#     y10data.append(y10)
#     y11data.append(y11)
#     y12data.append(y12)
#     # print(f'xdata={xdata} \ny1data={y1data} \ny2data={y2data} \ny3data={y3data} \ny4data={y4data} \ny5data={y5data} \ny6data={y6data} \y7data={y7data}\n')
#     dynamicUpdate.on_running(xdata, y1data, y2data, y3data, y4data, y5data, y6data, y7data, y8data, y9data, y10data, y11data, y12data)

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
