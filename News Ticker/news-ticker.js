var maxNewsHeadlines = 14
var maxInternationalHeadlines = 7
var maxSportHeadlines = 8
var newsTag = "新聞有線人及WhatsApp報料熱線：6333-3243"
var filteredKeywords= ["交易所直播室", "窩輪攻略", "一期一匯", "有線財經"]
var excludedCats = ["體育", "資訊節目（新聞）", "資訊節目", "推廣", "新聞通識", "資訊節目（財經）", "財經節目", "兩岸國際", "中國在線", "undefined"]
var internationalCats = ["中國在線", "兩岸國際"]
var sportHeaderText = "體育消息："
var firstTimeRunning = false

initiate()

function initiate() {
    var curTime = new Date();
    var nextUpdateTime = new Date(curTime.getFullYear(), curTime.getMonth(), curTime.getDate(), curTime.getHours(), (curTime.getMinutes() - (curTime.getMinutes() % 10)) + 10 - 1, 0, 0);
    var timeDiff = nextUpdateTime - curTime;
    if (timeDiff <= 0) {
        nextUpdateTime = new Date(nextUpdateTime.getTime() + 10*60000)
        var timeDiff = nextUpdateTime - curTime;
    }
    console.log("Next ticker update time: ");
    console.log(nextUpdateTime);
    console.log("Time diff: ");
    console.log(timeDiff);

    window.setTimeout(initiate, timeDiff);

    updateNewsTicker()
}


async function updateNewsTicker() {
    var newsHeadlines = await getNewsHeadlines()
    var sportHeadlines = await getSportHeadlines()

    newsHeadlines.forEach((element) => console.log(element));
    sportHeadlines.forEach((element) => console.log(element))

    const tickerMarquee = document.getElementById("ticker");

    // Remove all child
    tickerMarquee.innerHTML = '';

    newsHeadlines.forEach((newsItem) => {
        const span = document.createElement("span");
        span.innerHTML = newsItem;
        span.classList.add("news-item");""

        tickerMarquee.appendChild(span);
    })

    sportHeadlines.forEach((newsItem) => {
        const span = document.createElement("span");
        span.innerHTML = newsItem;
        span.classList.add("news-item");

        tickerMarquee.appendChild(span);
    })

    const span = document.createElement("span");
    span.innerHTML = newsTag;
    span.classList.add("news-item");

    tickerMarquee.appendChild(span);
}

function getNewsHeadlines() {
    return fetch("https://www.i-cable.com/graphql", {
        method: "POST",
        body: JSON.stringify({
            query: "      \n      query ($postId: [ID]) {\n        posts(first: 50, after: \"\", where:{\n          notIn: $postId,\n          orderby: {\n            field: DATE,\n            order: DESC\n          }\n        }) {\n          pageInfo {\n            hasPreviousPage\n            startCursor\n            hasNextPage\n            endCursor\n          }\n          edges {\n            node {\n              title\n              link\n              mainAndSubCategory {\n                main\n                sub\n              }\n            }\n          }\n        }\n      }\n    ",
            variables: {}
        }),
        headers: {
            'Accept': "application/json; text/plain; */*",
            'User-Agent': 'cableNews/3 CFNetwork/1410.0.3 Darwin/22.6.0',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json'
        }
    })
    .then((response) => response.json())
    .then((jsonObject) => {
        
        // Get news headlines (except for internal cats and excluded cats)
        var newsHeadlines = []

        for (var news of jsonObject['data']['posts']['edges']) {
            if ( news['node']['mainAndSubCategory'].length <= 0)
                var cat = "undefined"
            else
                var cat = news['node']['mainAndSubCategory'][0]['sub']

            if (!(excludedCats.includes(cat))) {
                var headlineString = news['node']['title']
                if  (!(filteredKeywords.some(v => headlineString.includes(v)))) {
                    headlineString = processHeadlineString(headlineString)
                    newsHeadlines.push(headlineString)
                }
            }
                    
            if (newsHeadlines.length >= maxNewsHeadlines)
                break
        }
        

        // Get international headlines
        var internationalHeadlines = []
        
        for (var news of jsonObject['data']['posts']['edges']) {
            if ( news['node']['mainAndSubCategory'].length <= 0)
                var cat = "undefined"
            else
                var cat = news['node']['mainAndSubCategory'][0]['sub']
            
            if (internationalCats.includes(cat)) {
                var headlineString = news['node']['title']
                if  (!(filteredKeywords.some(v => headlineString.includes(v)))) {
                    headlineString = processHeadlineString(headlineString)
                    internationalHeadlines.push(headlineString)
                }
            }
                    
            if (internationalHeadlines.length >= maxInternationalHeadlines)
                break
        }

        var output = newsHeadlines.concat(internationalHeadlines)

        return output
    });

}

function getSportHeadlines() {
    return fetch("https://www.i-cable.com/graphql", {
        method: "POST",
        body: JSON.stringify({
            query: "      \n      query getListsByCate($_category: Int) {\n        posts(first: 50, after: \"\", where:{categoryId: $_category}) {\n          pageInfo {\n            hasPreviousPage\n            startCursor\n            hasNextPage\n            endCursor\n          }\n          edges {\n            node {\n              title\n              link\n              mainAndSubCategory {\n                main\n                sub\n              }\n            }\n          }\n        }\n      }\n    ",
            variables: {"_category":321},
            operationName: "getListsByCate"
        }),
        headers: {
            'Accept': "application/json; text/plain; */*",
            'User-Agent': 'cableNews/3 CFNetwork/1410.0.3 Darwin/22.6.0',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json'
        }
    })
    .then((response) => response.json())
    .then((jsonObject) => {
        
        // Get sport headlines 
        var headerTextDisplayed = false
        var sportHeadlines = []

        for (var news of jsonObject['data']['posts']['edges']) {
            var headlineString = news['node']['title']
            if (!(filteredKeywords.some(v => headlineString.includes(v)))) {
                headlineString = processHeadlineString(headlineString)
                if (headerTextDisplayed == false) {
                    headlineString = sportHeaderText + headlineString
                    headerTextDisplayed = true
                }
                sportHeadlines.push(headlineString)
            }
                    
            if (sportHeadlines.length >= maxSportHeadlines)
                break
        }
        
        return sportHeadlines
    });

    
}

function processHeadlineString(headlineString) {
    headlineString = headlineString.replaceAll('　',' ')
    headlineString = headlineString.replaceAll(/\s+/g, ' ').trim()
    headlineString = headlineString.replaceAll(' │ ', '｜').replaceAll('|', '｜').replaceAll('︱', '｜')
    headlineString = headlineString.replaceAll(': ', '：')
    headlineString = headlineString.replaceAll('？ ', '？')
    headlineString = headlineString.replaceAll(',', '，')
    headlineString = headlineString.replaceAll(' ', '，')
    headlineString = headlineString.replaceAll(/^\，+|\，+$/g, '')
    headlineString = headlineString.replaceAll('｜', '：').replaceAll('【快訊】', '')
    return headlineString
}

function roundToNearest10(date = new Date()) {
    const minutes = 10;
    const ms = 1000 * 60 * minutes;

    return new Date(Math.ceil(date.getTime() / ms) * ms);
}
  
  



