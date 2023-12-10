from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def updateNewsStream():
    newsUpdateIntervalMin = 20
    
    url = 'https://www.i-cable.com/graphql'

    excludedCats = ["體育", "資訊節目（新聞）", "推廣", "新聞通識", "資訊節目（財經）", "undefined"]
    sportCats = ['體育']

    segment1ThresholdSec = 270.0
    segment2ThresholdSec = 40.0
    segment3ThresholdSec = 270.0
    segment4ThresholdSec = 40.0

    #Segment 1, 3 is for news; Segment 2, 4 is for Sports
    segment1List = []
    segment2List = [r'..\Idents, Bumpers, Placeholders\SportsNews_Bumper.ts']
    segment3List = []
    segment4List = [r'..\Idents, Bumpers, Placeholders\SportsNews_Bumper.ts']

    segment1Length = []
    segment2Length = []
    segment3Length = []
    segment4Length = []
    
    #Get the target time for download and merge video stream function

    targetTime = getTargetTime(newsUpdateIntervalMin)
    print(targetTime)
    print(targetTime + datetime.timedelta(minutes=10))

    #Let MCR know system is busy
    file = open(r'.\BackendStatus.txt', "w")
    file.write("Updating news database...")
    file.close()

    # Init webdriver for getVideoStream
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=r".\Chrome Driver\chromedriver.exe", options=options)

    #Get news streams

    myobj = {
                'query': "      \n      query ($postId: [ID]) {\n        posts(first: 50, after: \"\", where:{\n          notIn: $postId,\n          orderby: {\n            field: DATE,\n            order: DESC\n          }\n        }) {\n          pageInfo {\n            hasPreviousPage\n            startCursor\n            hasNextPage\n            endCursor\n          }\n          edges {\n            node {\n              title\n              link\n              mainAndSubCategory {\n                main\n                sub\n              }\n            }\n          }\n        }\n      }\n    ",
                'variables': {}
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
            newsLink = news['node']['link']
            videoURL = getVideoStream(newsLink, driver)
            if (videoURL != 'nil'):
                curLength = getVideoLength(videoURL)
                if (math.fsum(segment1Length) < segment1ThresholdSec):
                    segment1List.append(videoURL)
                    segment1Length.append(curLength)
                elif (math.fsum(segment3Length) < segment3ThresholdSec):
                    segment3List.append(videoURL)
                    segment3Length.append(curLength)
            
            if (math.fsum(segment1Length) >= segment1ThresholdSec) and (math.fsum(segment3Length) >= segment3ThresholdSec):
                break
    
    print("News Streams:")
    print("Segment 1: ")
    print(segment1List)
    print("Segment 3: ")
    print(segment3List)

    

    #Get sport streams
    myobj = {
                "query": "      \n      query getListsByCate($_category: Int) {\n        posts(first: 50, after: \"\", where:{categoryId: $_category}) {\n          pageInfo {\n            hasPreviousPage\n            startCursor\n            hasNextPage\n            endCursor\n          }\n          edges {\n            node {\n              title\n              link\n              mainAndSubCategory {\n                main\n                sub\n              }\n            }\n          }\n        }\n      }\n    ",
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
            newsLink = news['node']['link']
            videoURL = getVideoStream(newsLink, driver)
            if (videoURL != 'nil'):
                curLength = getVideoLength(videoURL)
                if (math.fsum(segment2Length) < segment2ThresholdSec):
                    segment2List.append(videoURL)
                    segment2Length.append(curLength)
                elif (math.fsum(segment4Length) < segment4ThresholdSec):
                    segment4List.append(videoURL)
                    segment4Length.append(curLength)

            if (math.fsum(segment2Length) >= segment2ThresholdSec) and (math.fsum(segment4Length) >= segment4ThresholdSec):
                break
    
    print("Sport Streams:")
    print("Segment 2: ")
    print(segment2List)
    print("Segment 4: ")
    print(segment4List)

    #Download Videos to respective folders

    #Let MCR know system is downloading news streams
    file = open(r'.\BackendStatus.txt', "w")
    file.write("Downloading news streams...")
    file.close()
    
    path = ".\\Video Source\\"

    downloadAndMergeVideo(segment1List, path, "segment1.mp4", "segment1Concat", targetTime)
    downloadAndMergeVideo(segment2List, path, "segment2.mp4", "segment2Concat", targetTime)
    downloadAndMergeVideo(segment3List, path, "segment3.mp4", "segment3Concat", targetTime)
    downloadAndMergeVideo(segment4List, path, "segment4.mp4", "segment4Concat", targetTime)

    #Unload Driver
    driver.quit()