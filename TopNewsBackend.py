import ffmpeg
import sys
import os
import shutil
import subprocess
import requests
import datetime
import time
import math
import re

backendStatusPath = r'.\BackendStatus.txt'

# MAIN FUNCTIONS

# CHECK FINANCE VISIBILITY FUNCTIONS
def checkFinanceWidgetVisiblity():
    financeWidgetVisibilityPath = r'.\Finance Widget\FinanceWidget-Visiblity.txt'
    currentTime = datetime.datetime.now() + datetime.timedelta(minutes=5)
    print(str(currentTime))
    print(str(currentTime.isoweekday()))
    print(str(currentTime.hour))
    if ((currentTime.isoweekday() == 6 and currentTime.hour >= 8) or (currentTime.isoweekday() == 7) or (currentTime.isoweekday() == 1 and currentTime.hour < 8)):
        with open(financeWidgetVisibilityPath, 'w', encoding='utf-8') as fp:
            fp.write("hide")
    else:
        with open(financeWidgetVisibilityPath, 'w', encoding='utf-8') as fp:
            fp.write("show")

# UPDATE WEATHER WIDGET FUNCTIONS
def updateWeatherWidget():

    weatherFormattedPath = r'.\Debug\Weather-Formatted.txt'
    currentTempPath = r".\Weather Widget\CurrentTemp.txt"
    currentHumidityPath = r".\Weather Widget\CurrentHumidity.txt"
    hswwIconFolder = r".\Weather Widget\Heat Stress at Work Icons"
    warningIconFolder = r".\Weather Widget\Warning Icons"
    forecastIconFolder = r".\Weather Widget\Forecast Icons"
    currentWxIconsFolder = r".\Weather Widget"
    currentWxIconsFilePrefix = "CurrentIcon"
    blankIconPath = r".\Weather Widget\blank.png"
    maxIcons = 6

    wxReportAPI = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en"
    warnSumAPI = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en"
    hswwAPI = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=hsww&lang=en"

    file = open(backendStatusPath, "w")
    file.write("Updating weather widget")
    file.close()

    weatherIcons = []
    weatherWarnCodes = []

    iconID = 0

    weatherWarns = {
        "WTMW": False,
        "TC1": False,
        "TC3": False,
        "TC8NE": False,
        "TC8SE": False,
        "TC8NW": False,
        "TC8SW": False,
        "TC9": False,
        "TC10": False,
        "WRAINA": False,
        "WRAINR": False,
        "WRAINB": False,
        "WTS": False,
        "WHOT": False,
        "WCOLD": False,
        "WFIREY": False,
        "WFIRER": False,
        "WFROST": False,
        "WMSGNAL": False,
        "WL": False,
        "WFNTSA": False
    }

    #Update current temp and humidity
    currentTemp = 0
    currentHumidity = 0

    try:
        wxReport = requests.get(wxReportAPI).json()

        for i in range(0, len(wxReport["temperature"]["data"])):
            if (wxReport["temperature"]["data"][i]["place"] == "Hong Kong Observatory"):
                currentTemp = wxReport["temperature"]["data"][i]["value"]
                break
        
        for i in range(0, len(wxReport["humidity"]["data"])):
            if (wxReport["humidity"]["data"][i]["place"] == "Hong Kong Observatory"):
                currentHumidity = wxReport["humidity"]["data"][i]["value"]
                break

    except Exception as err:
        print("An error occured while fetching wxReport API: " + type(err).__name__)
        print(str(err))

        wxReport = []
    

    with open(currentTempPath, "w", encoding="utf-8") as file:
        file.write(str(currentTemp) + "°C")

    with open(currentHumidityPath, "w") as file:
        file.write(str(currentHumidity) + "%")


    #Update heat stress at work warning

    try:
        #hsww = json.loads('{ "hsww": { "desc": "A reminder from the Labour Department: Amber Heat Stress at Work Warning is in effect today at 11:00 am, indicating that the heat stress in some work environments is high. Please take appropriate heat preventive measures.",  "warningLevel": "AMBER", "actionCode": "ISSUE", "effectiveTime": "2020-05-15T11:00:00+08:00", "issueTime": "2020-05-15T10:55:00+08:00" }}')
        hsww =  requests.get(hswwAPI).json()

        if "hsww" in hsww:
            hswwWarning = hsww['hsww']['warningLevel']
            if (hswwWarning != ""):
                icon = hswwIconFolder + "\\" + hswwWarning + ".png"
                weatherIcons.append(icon)
                weatherWarnCodes.append("HSWW_"+hswwWarning)
        else:
            hswwWarning = ""

    except Exception as err:

        if (type(err).__name__ == "JSONDecodeError"):
            hswwWarning = ""
        else:
            print("An error occured while fetching hsww API: " + type(err).__name__)
            print(str(err))
            hswwWarning = ""


    #Update weather warnings

    try:
        warnSum = requests.get(warnSumAPI).json()

        for cat in warnSum:
            if (warnSum[cat]["actionCode"] != "CANCEL"):
                code = warnSum[cat]["code"]
                weatherWarns[code] = True
    
    except Exception as err:
        print("An error occured while fetching warnSum API: " + type(err).__name__)
        print(str(err))

        warnSum = []


    #Update current forecast weather icon
    if ("icon" in wxReport):
        iconID = wxReport["icon"][0]

    #Assign weather icons
    for key in weatherWarns:
        if weatherWarns[key] == True:
            icon = warningIconFolder+"\\"+key+".png"
            weatherIcons.append(icon)
            weatherWarnCodes.append(key)
            if (len(weatherIcons) >= 5):
                break
    
    icon = forecastIconFolder + "\\pic" + str(iconID) + ".png"
    if (len(weatherIcons) <= 5):
        weatherIcons.append(icon)

    #Update weather icons

    for i in range(0, len(weatherIcons)):
        id = i + 1
        destPath = currentWxIconsFolder + "\\" + currentWxIconsFilePrefix + str(id) + ".png"
        shutil.copyfile(weatherIcons[i], destPath)

    #Replace the rest with blank icons

    for i in range(len(weatherIcons), maxIcons):
        id = i + 1
        destPath = currentWxIconsFolder + "\\" + currentWxIconsFilePrefix + str(id) + ".png"
        shutil.copyfile(blankIconPath, destPath)

    #Update current weather warnings
    print()
    print("Latest Weather:")
    print("Current Temperature: " + str(currentTemp) + "°C")
    print("Current Humidity: " + str(currentHumidity) + "%")
    print("Current Weather Warning Codes: " + str(weatherWarnCodes))
    print("Current Forecast ID: " + str(iconID))

    #Write to debug log
    currentTime = datetime.datetime.now()
    with open(weatherFormattedPath, 'w', encoding='utf-8') as fp:
        fp.write("Current Temperature: " + str(currentTemp) + "°C\n")
        fp.write("Current Humidity: " + str(currentHumidity) + "%\n")
        fp.write("Current Weather Warning Codes: " + str(weatherWarnCodes)+"\n")
        fp.write("Current Forecast ID: " + str(iconID)+"\n")
        fp.write("\nLast updated: " + str(currentTime))

# UPDATE NEWS TICKER FUNCTIONS

def processHeadlineString(headlineString):

    headlineString = headlineString.replace("　", " ")
    headlineString = " ".join(headlineString.split())
    headlineString = headlineString.replace(' │ ', '｜').replace('|', '｜').replace('︱','｜')
    headlineString = headlineString.replace(': ', '：')
    headlineString = headlineString.replace('？ ', '？')
    headlineString = headlineString.replace(',', '，')
    headlineString = headlineString.replace(' ', '，')
    headlineString = "，".join(headlineString.split())
    headlineString = headlineString.replace('｜', '：').replace('【快訊】', '')
    
    return headlineString

def updateNewsTicker():

    newsTickerPath = r'.\NewsTicker.txt'
    newsTickerFormattedPath = r'.\Debug\NewsTicker-Formatted.txt'

    #Let MCR know system is busy
    file = open(backendStatusPath, "w")
    file.write("Updating news ticker...")
    file.close()

    url = 'https://www.i-cable.com/graphql'

    maxNewsHeadlines = 14
    maxInternationalHeadlines = 7
    maxSportHeadlines = 8
    newsTag = "新聞有線人及WhatsApp報料熱線：6333-3243"
    filteredKeywords= ["交易所直播室", "窩輪攻略", "一期一匯", "有線財經"]
    excludedCats = ["體育", "資訊節目（新聞）", "資訊節目", "推廣", "新聞通識", "資訊節目（財經）", "財經節目", "兩岸國際", "中國在線", "undefined"]
    internationalCats = ["中國在線", "兩岸國際"]
    sportHeaderText = "體育消息："

    #Get news headlines (except for internal cats and excluded cats)

    myobj = {
                "query": "      \n      query ($postId: [ID]) {\n        posts(first: 50, after: \"\", where:{\n          notIn: $postId,\n          orderby: {\n            field: DATE,\n            order: DESC\n          }\n        }) {\n          pageInfo {\n            hasPreviousPage\n            startCursor\n            hasNextPage\n            endCursor\n          }\n          edges {\n            node {\n              title\n              date\n              link\n              mainAndSubCategory {\n                main\n                sub\n              }\n            }\n          }\n        }\n      }\n    ",
                "variables": {}
            }

    headers = {'Content-Type' : 'application/json'}

    x = requests.post(url = url, json = myobj, headers = headers)
    jsonObject = x.json()

    newsHeadlines = []
    
   
    for news in jsonObject['data']['posts']['edges']:
        if (len(news['node']['mainAndSubCategory']) <= 0):
            cat = "undefined"
        else: 
            cat = news['node']['mainAndSubCategory'][0]['sub']

        if cat not in excludedCats:
            headlineString = news['node']['title']
            if not (any(ext in headlineString for ext in filteredKeywords)):
                headlineString = processHeadlineString(headlineString)
                newsHeadlines.append(headlineString)
                
        if (len(newsHeadlines) >= maxNewsHeadlines):
            break

    #Get international headlines

    
    internationalHeadlines = []

    for news in jsonObject['data']['posts']['edges']:
        if (len(news['node']['mainAndSubCategory']) <= 0):
            cat = "undefined"
        else: 
            cat = news['node']['mainAndSubCategory'][0]['sub']

        if cat in internationalCats:
            headlineString = news['node']['title']
            if not (any(ext in headlineString for ext in filteredKeywords)):
                headlineString = processHeadlineString(headlineString)
                internationalHeadlines.append(headlineString)
        if (len(internationalHeadlines) >= maxInternationalHeadlines):
            break

    #Get sports headlines

    myobj = {
                "query": "      \n      query getListsByCate($_category: Int) {\n        posts(first: 50, after: \"\", where:{categoryId: $_category}) {\n          pageInfo {\n            hasPreviousPage\n            startCursor\n            hasNextPage\n            endCursor\n          }\n          edges {\n            node {\n              title\n              date\n              link\n              mainAndSubCategory {\n                main\n                sub\n              }\n            }\n          }\n        }\n      }\n    ",
                "variables": {"_category":321},
                "operationName":"getListsByCate"
            }

    headers = {'Content-Type' : 'application/json'}

    x = requests.post(url = url, json = myobj, headers = headers)
    jsonObject = x.json()
    
    headerTextDisplayed = False
    sportHeadlines = []

    for news in jsonObject['data']['posts']['edges']:
        headlineString = news['node']['title']
        if not (any(ext in headlineString for ext in filteredKeywords)):
            headlineString = processHeadlineString(headlineString)
            if (headerTextDisplayed == False):
                headlineString = sportHeaderText + headlineString
                headerTextDisplayed = True
            sportHeadlines.append(headlineString)

        if (len(sportHeadlines) >= maxSportHeadlines):
            break

    #Write result to txt

    with open(newsTickerPath, 'w', encoding='utf-8') as fp:
        for item in newsHeadlines:
            # write each item on a new line
            fp.write("%s          " % item)
        for item in internationalHeadlines:
            # write each item on a new line
            fp.write("%s          " % item)
        for item in sportHeadlines:
            # write each item on a new line
            fp.write("%s          " % item)
        fp.write("%s          " % newsTag)
        fp.write("          ")


    #Print debug
    print()
    print("Latest Headlines:")
    print("---")

    for i in newsHeadlines:
        print(i)

    print("---")

    for i in internationalHeadlines:
        print(i)

    print("---")

    for i in sportHeadlines:
        print(i)

    print("---")
    print(newsTag)


    #Write result to debug

    currentTime = datetime.datetime.now()
    
    with open(newsTickerFormattedPath, 'w', encoding='utf-8') as fp:
        for item in newsHeadlines:
            # write each item on a new line
            fp.write("%s\n" % item)
        fp.write("\n")
        for item in internationalHeadlines:
            # write each item on a new line
            fp.write("%s\n" % item)
        fp.write("\n")
        for item in sportHeadlines:
            # write each item on a new line
            fp.write("%s\n" % item)
        fp.write("\n")
        fp.write("%s\n" % newsTag)
        fp.write("\nLast updated: " + str(currentTime))
    
    print('Done')



# UPDATE NEWS STREAM FUNCTIONS

def isVideoURLReady(url):
    response = requests.head(url)
    if (response.status_code == 200):
        return True
    else:
        return False

def validateVideoLength(url, maxSeconds):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', url], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if (float(result.stdout) <= maxSeconds):
        return True
    else:
        return False
    
def getVideoLength(url):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', url], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)
    
def downloadVideo(url, fileName):
    print("Downloading " + url + " to " + fileName)
    test = ffmpeg.input(url)
    test2 = test.output(fileName)
    test2.run(overwrite_output=True)
            
def downloadAndMergeVideo(urlList, path, fileName, concatListName, targetTime):    

    mcrCurrentlyPlayingPath = ".\\MCRCurrentlyPlaying.txt"

    if (len(urlList) <= 0):
        print("There are no video streams in " + concatListName + ", cannot merge streams")
        return

    filePath = path + fileName

    with open(mcrCurrentlyPlayingPath) as f:
        
        while (f.read() == fileName):
            print("MCR currently playing " + fileName + ", waiting until playback finishes...")
            f.seek(0)
            file = open(backendStatusPath, "w")
            file.write("Waiting for " + fileName + " to finish playing...")
            file.close()
            time.sleep(5)

    file = open(backendStatusPath, "w")
    file.write("Writing " + fileName)
    file.close()        

    concatFilePath = path + concatListName + ".txt"
    print("Downloading the following: ")
    print("and merging into " + fileName)
    
    open(concatFilePath, "w").writelines([("file '%s'\n" % url) for url in urlList])
    
    try:
        ffmpeg.input(concatFilePath, format='concat', safe=0, protocol_whitelist="tcp,tls,https,file,crypto,data").output(filePath, acodec="aac", vcodec="copy", ar=44100).run(overwrite_output=True)
    except Exception as error:
        print("Error when merging " + fileName + ": ")
        print(str(error))
        file = open(backendStatusPath, "w")
        file.write("Error merging " + fileName)
        file.close()     
        time.sleep(10)

    #Check time if it's late for segment1.mp4. If late, send a command to MCR to start immediately.

    currentTime = datetime.datetime.now()
    
    if (fileName == "segment1.mp4"):    
        if (currentTime > targetTime):
            file = open(backendStatusPath, "w")
            file.write("Late start on " + fileName)
            file.close()       
            time.sleep(5)

    elif (fileName == "segment3.mp4"):
        if (currentTime > (targetTime + datetime.timedelta(minutes=10))):
            file = open(backendStatusPath, "w")
            file.write("Late start on " + fileName)
            file.close()       
            time.sleep(5)

def getVideoStream(videoUrl):
    maximumNewsItemLength = 220

    print('\nObtaining video stream from "' + videoUrl + '"...')

    try:
        videoTitle = ""

        if (videoUrl != ''):
            if ('.mp4/playlist.m3u8' in videoUrl.lower()):
                if ('iottvideosrc/news' in videoUrl.lower()):
                    result = re.search('https://uc6.i-cable.com/vod_freedirectbasic/_definst_/joemud/newsotto/iottvideosrc/news/(.*).mp4/playlist.m3u8', videoUrl, re.IGNORECASE)
                    if not (result is None):
                        videoTitle = result.group(1)
                elif ('iottvideosrc/fin' in videoUrl.lower()):
                    result = re.search('https://uc6.i-cable.com/vod_freedirectbasic/_definst_/joemud/newsotto/iottvideosrc/fin/(.*).mp4/playlist.m3u8', videoUrl, re.IGNORECASE)
                    if not (result is None):
                        videoTitle = result.group(1)
                else:
                    result = re.search('https://uc6.i-cable.com/vod_freedirectbasic/_definst_/joemud/newsotto/iottvideosrc(.*).mp4/playlist.m3u8', videoUrl, re.IGNORECASE)
                    if not (result is None):
                        videoTitle = result.group(1)
            else:
                if ('iottvideosrc/news' in videoUrl.lower()):
                    result = re.search('https://uc6.i-cable.com/vod_freedirectbasic/_definst_/joemud/newsotto/iottvideosrc/news/(.*).mp3/playlist.m3u8', videoUrl, re.IGNORECASE)
                    if not (result is None):
                        videoTitle = result.group(1)
                elif ('iottvideosrc/fin' in videoUrl.lower()):
                    result = re.search('https://uc6.i-cable.com/vod_freedirectbasic/_definst_/joemud/newsotto/iottvideosrc/fin/(.*).mp3/playlist.m3u8', videoUrl, re.IGNORECASE)
                    if not (result is None):
                        videoTitle = result.group(1)
                else:
                    result = re.search('https://uc6.i-cable.com/vod_freedirectbasic/_definst_/joemud/newsotto/iottvideosrc(.*).mp3/playlist.m3u8', videoUrl, re.IGNORECASE)
                    if not (result is None):
                        videoTitle = result.group(1)

        streamUrl = "https://vod.i-cable.com/" + videoTitle + "/NEWSHLS/" + videoTitle + ".m3u8"
        print(streamUrl)

        if (isVideoURLReady(streamUrl) != True):
            print("Stream URL not ready yet!")
            return "nil"
        elif (validateVideoLength(streamUrl, maximumNewsItemLength) != True):
            print("Video is longer than the preset maximum length of " + str(maximumNewsItemLength) + " seconds!")
            return "nil"
        else:
            return streamUrl
        
    except Exception as e:
        print("An error occured while obtaining stream URL!")
        print(e)
        return "nil"

def getTargetTime(interval):
    currentTime = datetime.datetime.now()
    targetTime = currentTime + (datetime.datetime.min - currentTime) % datetime.timedelta(minutes=interval)
    return targetTime

def updateNewsStream():
    newsUpdateIntervalMin = 20
    
    url = 'https://www.i-cable.com/graphql'
    sportsNewsBumperPath = r'..\Idents, Bumpers, Placeholders\SportsNews_Bumper.ts'
    videoSourcePath = ".\\Video Source\\"
    newsStreamFormattedPath = r'.\Debug\NewsStream-Formatted.txt'

    excludedCats = ["體育", "資訊節目（新聞）",  "資訊節目", "推廣", "新聞通識", "資訊節目（財經）", "財經節目", "undefined"]
    sportCats = ['體育']

    segment1ThresholdSec = 270.0
    segment2ThresholdSec = 40.0
    segment3ThresholdSec = 270.0
    segment4ThresholdSec = 40.0

    #Segment 1, 3 is for news; Segment 2, 4 is for Sports
    segment1List = []
    segment2List = [sportsNewsBumperPath]
    segment3List = []
    segment4List = [sportsNewsBumperPath]

    segment1Length = []
    segment2Length = []
    segment3Length = []
    segment4Length = []

    #Mark start time for time stamp
    startTime = datetime.datetime.now()
    
    #Get the target time for download and merge video stream function
    targetTime = getTargetTime(newsUpdateIntervalMin)
    print("Target time: " + str(targetTime))

    #Let MCR know system is busy
    file = open(backendStatusPath, "w")
    file.write("Updating news database...")
    file.close()

    #Get news streams

    myobj = {
                "query": "      \n      query ($postId: [ID]) {\n        posts(first: 50, after: \"\", where:{\n          notIn: $postId,\n          orderby: {\n            field: DATE,\n            order: DESC\n          }\n        }) {\n          pageInfo {\n            hasPreviousPage\n            startCursor\n            hasNextPage\n            endCursor\n          }\n          edges {\n            node {\n              title\n              date\n              link\n              videoUrl\n              mainAndSubCategory {\n                main\n                sub\n              }\n            }\n          }\n        }\n      }\n    ",
                "variables": {}
            }

    headers = {
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'cableNews/3 CFNetwork/1410.0.3 Darwin/22.6.0',
                'Accept-Language': 'en-GB,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }

    x = requests.post(url = url, json = myobj, headers = headers)


    jsonObject = x.json()
    
    for news in jsonObject['data']['posts']['edges']:
        if (len(news['node']['mainAndSubCategory']) <= 0):
            cat = "undefined"
        else: 
            cat = news['node']['mainAndSubCategory'][0]['sub']

        if cat not in excludedCats:
            videoUrl = news['node']['videoUrl']
            streamUrl = 'nil'
            if (videoUrl != ''):   
                streamUrl = getVideoStream(videoUrl)
            if (streamUrl != 'nil'):
                curLength = getVideoLength(streamUrl)
                if (math.fsum(segment1Length) < segment1ThresholdSec):
                    segment1List.append(streamUrl)
                    segment1Length.append(curLength)
                elif (math.fsum(segment3Length) < segment3ThresholdSec):
                    segment3List.append(streamUrl)
                    segment3Length.append(curLength)
            
            if (math.fsum(segment1Length) >= segment1ThresholdSec) and (math.fsum(segment3Length) >= segment3ThresholdSec):
                break
    
    

    #Get sport streams
    myobj = {
                "query": "      \n      query getListsByCate($_category: Int) {\n        posts(first: 50, after: \"\", where:{categoryId: $_category}) {\n          pageInfo {\n            hasPreviousPage\n            startCursor\n            hasNextPage\n            endCursor\n          }\n          edges {\n            node {\n              title\n              link\n              videoUrl\n              mainAndSubCategory {\n                main\n                sub\n              }\n            }\n          }\n        }\n      }\n    ",
                "variables": {"_category":321},
                "operationName":"getListsByCate"
            }

    headers = {
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'cableNews/3 CFNetwork/1410.0.3 Darwin/22.6.0',
                'Accept-Language': 'en-GB,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
    
    
    x = requests.post(url = url, json = myobj, headers = headers)

    jsonObject = x.json()
    
    for news in jsonObject['data']['posts']['edges']:
        if (len(news['node']['mainAndSubCategory']) <= 0):
            cat = "undefined"
        else: 
            cat = news['node']['mainAndSubCategory'][0]['sub']

        if cat in sportCats:
            videoUrl = news['node']['videoUrl']
            streamUrl = 'nil'
            if (videoUrl != ''):   
                streamUrl = getVideoStream(videoUrl)
            if (streamUrl != 'nil'):
                curLength = getVideoLength(streamUrl)
                if (math.fsum(segment2Length) < segment2ThresholdSec):
                    segment2List.append(streamUrl)
                    segment2Length.append(curLength)
                elif (math.fsum(segment4Length) < segment4ThresholdSec):
                    segment4List.append(streamUrl)
                    segment4Length.append(curLength)

            if (math.fsum(segment2Length) >= segment2ThresholdSec) and (math.fsum(segment4Length) >= segment4ThresholdSec):
                break

    #Download Videos to respective folders

    #Let MCR know system is downloading news streams
    file = open(backendStatusPath, "w")
    file.write("Downloading news streams...")
    file.close()
    
    path = videoSourcePath

    downloadAndMergeVideo(segment1List, path, "segment1.mp4", "segment1Concat", targetTime)
    downloadAndMergeVideo(segment2List, path, "segment2.mp4", "segment2Concat", targetTime)
    downloadAndMergeVideo(segment3List, path, "segment3.mp4", "segment3Concat", targetTime)
    downloadAndMergeVideo(segment4List, path, "segment4.mp4", "segment4Concat", targetTime)

    # Mark end time
    endTime = datetime.datetime.now()
    elapsedTime = endTime - startTime

    # Print debug

    print()
    print("News Streams:\n")
    print("Segment 1: ")
    for stream in segment1List:
        print(stream)
    print("Total length: " + str(datetime.timedelta(seconds = math.fsum(segment1Length)))+"\n")
    
    print("Segment 3:")
    for stream in segment3List:
        print(stream)
    print("Total length: " + str(datetime.timedelta(seconds = math.fsum(segment3Length))) + "\n")

    print("Sport Streams:\n")
    print("Segment 2:")
    for stream in segment2List:
        print(stream)
    print("Total length: " + str(datetime.timedelta(seconds = math.fsum(segment2Length)))+"\n")

    print("Segment 4: ")
    for stream in segment4List:
        print(stream)
    print("Total length: " + str(datetime.timedelta(seconds = math.fsum(segment4Length)))+"\n")

    print("Last updated: " + str(endTime))
    print("Elapsed time: " + str(elapsedTime))

    #Write result to debug
    with open(newsStreamFormattedPath, 'w') as fp:
        fp.write("Segment 1:\n")
        for stream in segment1List:
            # write each item on a new line
            fp.write("%s\n" % stream)
        fp.write("Total length: " + str(datetime.timedelta(seconds = math.fsum(segment1Length))) + "\n" )

        fp.write("\nSegment 2:\n")
        for stream in segment2List:
            # write each item on a new line
            fp.write("%s\n" % stream)
        fp.write("Total length: " + str(datetime.timedelta(seconds = math.fsum(segment2Length))) + "\n" )

        fp.write("\nSegment 3:\n")
        for stream in segment3List:
            # write each item on a new line
            fp.write("%s\n" % stream)
        fp.write("Total length: " + str(datetime.timedelta(seconds = math.fsum(segment3Length))) + "\n" )

        fp.write("\nSegment 4:\n")
        for stream in segment4List:
            # write each item on a new line
            fp.write("%s\n" % stream)
        fp.write("Total length: " + str(datetime.timedelta(seconds = math.fsum(segment4Length))) + "\n" )

        fp.write("\nLast updated: " + str(endTime)+"\n")
        fp.write("Elapsed time: " + str(elapsedTime)+"\n")
  
# MAIN FUNCTION

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#Special Commands: "wxOnly", "tickerOnly", "wx&tickerOnly"

specialCommands = ""

if (len(sys.argv) > 1):
    specialCommands = str(sys.argv[1])

if (specialCommands == "wxOnly"):
    updateWeatherWidget()

elif (specialCommands == "tickerOnly"):
    updateNewsTicker()

elif (specialCommands == "wx&tickerOnly"):
    updateWeatherWidget()
    updateNewsTicker()

else:

    try:
        checkFinanceWidgetVisiblity()
    except Exception as e:
        print("Error in checking finance widget visibility: ")
        print(e)
        file = open(backendStatusPath, "w")
        file.write("Error in checking finance widget visibility")
        file.close()
        time.sleep(5)


    try:
        updateWeatherWidget()
    except Exception as e:
        print("Error in updating weather widget: ")
        print(e)
        file = open(backendStatusPath, "w")
        file.write("Error in updating weather widget")
        file.close()
        time.sleep(5)

    try:
        updateNewsTicker()
    except Exception as e:
        print("Error in updating news ticker: ")
        print(e)
        file = open(backendStatusPath, "w")
        file.write("Error in updating news ticker")
        file.close()
        time.sleep(5)

    try:
        updateNewsStream()
    except Exception as e:
        print("Error in updating news stream: ")
        print(e)
        file = open(backendStatusPath, "w")
        file.write("Error in updating news stream")
        file.close()
        time.sleep(5)


    #path = ".\\Video Source\\"
    #targetTime = getTargetTime(20)
    #segment2List = [r'..\Idents, Bumpers, Placeholders\SportsNews_Bumper.ts', 'https://vod.i-cable.com/N_20231004_(AG)FOOTBALL-2200(WED)_logo/NEWSHLS/N_20231004_(AG)FOOTBALL-2200(WED)_logo.m3u8']
    #downloadAndMergeVideo(segment2List, path, "segment2.mp4", "segment2Concat", targetTime)


#Let MCR know update has finished

file = open(backendStatusPath, "w")
file.write("Ready")
file.close()

sys.exit()