def getVideoStream(contentUrl, driver):
    
    maximumNewsItemLength = 220

    print('\nObtaining video link from "' + contentUrl + '"...')

    # implicit wait applied
    driver.get(contentUrl)
    # to identify element and obtain innerHTML with get_attribute
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 
    'content-video')))
        content = driver.find_element_by_id('content-video')
        #print(test)
        #print(content)
        videoURL = content.get_attribute("data-url")
        print(videoURL)
        if (isVideoURLReady(videoURL) != True):
            print("Video URL not ready yet!")
            return "nil"
        elif (validateVideoLength(videoURL, maximumNewsItemLength) != True):
            print("Video is longer than the preset maximum length of " + str(maximumNewsItemLength) + " seconds!")
            return "nil"
        else:
            return videoURL
    except Exception as e:
        print(e)
        print("No video URL found!")
        return "nil"