var symbol = ['^HSI', '000300.SS', '000001.SS', '^DJI', '^GSPC', '^FTSE', '^FCHI', '^N225', 'GC=F']
var price = ['0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00']
var change = ['0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '']
var changeSymbol = ['', '', '', '', '', '', '', '', '']

var header_Chi = ["恆指", "滬深", "上證", "道指", "標普", "富時", "CAC", "日本", "現貨金"];
var header_Eng = ["HSI", "CSI", "SSE", "DJIA", "S&P", "FTSE", "CAC", "NI225", "GOLD"];

var counter = 0;
var header_chi_text = document.getElementById("Header_Chi");
var header_eng_text = document.getElementById("Header_Eng");
var price_text = document.getElementById("Price");
var change_text = document.getElementById("Change");
var change_symbol_text = document.getElementById("ChangeSymbol")
var val = document.getElementById("Value");
const delay = ms => new Promise(res => setTimeout(res, ms));
var baseTimeoutDelay = 5000
var timeoutDelay = baseTimeoutDelay



updateUI(counter)
counter++
updateStockInfo()

setInterval(function () {
    if (counter >= symbol.length) {
        counter = 0
        // clearInterval(inst); // uncomment this if you want to stop refreshing after one cycle
    }

    updateUI(counter)

    counter++;   

}, 8000)

setInterval(updateStockInfo, 120000)

async function updateStockInfo() {

    // Update stock set
    updateStockSet()
    
    // Get Stocks
    for (var i = 0; i < symbol.length; i++) {
        var jsonObject = await getStockInfo(symbol[i]);
        if (jsonObject != "Error") {
            price[i] = jsonObject["quoteSummary"]["result"][0]["price"]["regularMarketPrice"]["fmt"]
            if (symbol[i] != 'GC=F') {
                change[i] = jsonObject["quoteSummary"]["result"][0]["price"]["regularMarketChange"]["fmt"]
                if (change[i] == "0.00") {
                    changeSymbol[i] = ""
                }
                else if (change[i].includes("-")) {
                    changeSymbol[i] = "▼"
                    change[i] = change[i].replace("-", "")
                }
                else {
                    changeSymbol[i] = "▲"
                }
            }

            // Change HTML DOM

            if ((counter-1) == i) {
                updateUI((counter-1))
            }

            if (timeoutDelay != baseTimeoutDelay) {
                timeoutDelay = baseTimeoutDelay
            }

            await delay(2000)
           
        }
        else {
            
            // If fail, re-fetch data
            console.log("Cannot update data for " + symbol[i] + ", re-fetching data...");
            
            i = i - 1;

            await delay(timeoutDelay)

            timeoutDelay = timeoutDelay + baseTimeoutDelay

            /*
            price[i] = "0.00"
            if (i < 6) {
                change[i] = "0.00"
                changeSymbol[i] = ""
            }
            */
        }
        
    }

}

function getStockInfo(stockCode) {
    
    url = "https://query1.finance.yahoo.com/v6/finance/quoteSummary/" + stockCode + "?modules=price"

    return fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`)
    .then(response => {
        if (response.status == 200) {
            return response.json()
        } 
        else
            return "Error"
    
    })
    .then(jsonObject => {
        return JSON.parse(jsonObject["contents"])

    })
    .catch((error) => {
        return "Error"
      });

}

function updateUI(id) {
    header_chi_text.innerHTML = header_Chi[id];
    header_eng_text.innerHTML = header_Eng[id];
    price_text.innerHTML = price[id];
    change_text.innerHTML = change[id];
    change_symbol_text.innerHTML = changeSymbol[id];

    if (changeSymbol[id] == "▲") {
        change_symbol_text.style.color = "green"
    }
    else if (changeSymbol[id] == "▼") {
        change_symbol_text.style.color = "red"
    }
    else {
        change_symbol_text.style.color = "white"
    }
    
}

function isCurrentTimeInBetween(startTime, endTime) {
    currentDate = new Date()   

    startDate = new Date(currentDate.getTime());
    startDate.setHours(startTime.split(":")[0]);
    startDate.setMinutes(startTime.split(":")[1]);
    startDate.setSeconds(startTime.split(":")[2]);

    endDate = new Date(currentDate.getTime());
    endDate.setHours(endTime.split(":")[0]);
    endDate.setMinutes(endTime.split(":")[1]);
    endDate.setSeconds(endTime.split(":")[2]);


    valid = startDate <= currentDate && endDate >= currentDate
    return valid
}

function updateStockSet() {
    if (isCurrentTimeInBetween('00:00:00', '07:59:59')) {
        symbol = ['^DJI', '^GSPC', '^FTSE', '^FCHI', 'GC=F']
        price = ['0.00', '0.00', '0.00', '0.00', '0.00']
        change = ['0.00', '0.00', '0.00', '0.00', '']
        changeSymbol = ['', '', '', '', '']
    
        header_Chi = ["道指", "標普", "富時", "CAC", "現貨金"];
        header_Eng = ["DJIA", "S&P", "FTSE", "CAC", "GOLD"];
    }
    else if (isCurrentTimeInBetween('08:00:00', '09:29:59')) {
        symbol = ['^DJI', '^GSPC', '^N225', 'GC=F']
        price = ['0.00', '0.00', '0.00', '0.00']
        change = ['0.00', '0.00', '0.00', '']
        changeSymbol = ['', '', '', '']
    
        header_Chi = ["道指", "標普", "日本", "現貨金"];
        header_Eng = ["DJIA", "S&P", "NI225", "GOLD"];
    }
    else if (isCurrentTimeInBetween('09:30:00', '16:29:59')) {
        symbol = ['^HSI', '000300.SS', '000001.SS', 'GC=F']
        price = ['0.00', '0.00', '0.00', '0.00']
        change = ['0.00', '0.00', '0.00', '']
        changeSymbol = ['', '', '', '']
    
        header_Chi = ["恆指", "滬深", "上證", "現貨金"];
        header_Eng = ["HSI", "CSI", "SSE", "GOLD"];
    }
    else if (isCurrentTimeInBetween('16:30:00', '16:59:59')) {
        symbol = ['^HSI', '^FTSE', '^FCHI', 'GC=F']
        price = ['0.00', '0.00', '0.00', '0.00']
        change = ['0.00', '0.00', '0.00', '']
        changeSymbol = ['', '', '', '']
    
        header_Chi = ["恆指", "富時", "CAC", "現貨金"];
        header_Eng = ["HSI", "FTSE", "CAC", "GOLD"];
    }
    else if (isCurrentTimeInBetween('17:00:00', '21:29:59')) {
        symbol = ['^FTSE', '^FCHI', 'GC=F']
        price = ['0.00', '0.00', '0.00']
        change = ['0.00', '0.00', '']
        changeSymbol = ['', '', '']
    
        header_Chi = ["富時", "CAC", "現貨金"];
        header_Eng = ["FTSE", "CAC", "GOLD"];
    }
    else if (isCurrentTimeInBetween('21:30:00', '23:59:59')) {
        symbol = ['^DJI', '^GSPC', '^FTSE', '^FCHI', 'GC=F']
        price = ['0.00', '0.00', '0.00', '0.00', '0.00']
        change = ['0.00', '0.00', '0.00', '0.00', '']
        changeSymbol = ['', '', '', '', '']
    
        header_Chi = ["道指", "標普", "富時", "CAC", "現貨金"];
        header_Eng = ["DJIA", "S&P", "FTSE", "CAC", "GOLD"];
    }
    
}