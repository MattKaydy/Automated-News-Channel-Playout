def updateFinanceWidget():

    #If an instance is currently open updating top news, don't run
    with open(r'.\BackendStatus.txt', 'r') as file:
        data = file.readlines()
        if data[0] != "Ready":
            return


    #Let MCR know system is busy
    file = open(r'.\BackendStatus.txt', "w")
    file.write("Updating finance widget...")
    file.close()

    financeScriptPath = r".\Finance Widget\finance-script.js"

    tickers = yahooFinance.Tickers("^HSI ^DJI ^GSPC ^FTSE ^FCHI ^N225 GC=F")
    
    HSI = tickers.tickers["^HSI"].fast_info
    DJIA = tickers.tickers["^DJI"].fast_info
    SNP = tickers.tickers["^GSPC"].fast_info
    FTSE = tickers.tickers["^FTSE"].fast_info
    CAC = tickers.tickers["^FCHI"].fast_info
    NI225 = tickers.tickers["^N225"].fast_info
    GOLD = tickers.tickers["GC=F"].fast_info
    
    prices = [
        "{0:,.2f}".format(HSI["lastPrice"]),
        "{0:,.2f}".format(DJIA["lastPrice"]),
        "{0:,.2f}".format(SNP["lastPrice"]),
        "{0:,.2f}".format(FTSE["lastPrice"]),
        "{0:,.2f}".format(CAC["lastPrice"]),
        "{0:,.2f}".format(NI225["lastPrice"]),
        "{0:,.2f}".format(GOLD["lastPrice"]),
    ]

    change_raw = [
        (HSI["lastPrice"] - HSI["previousClose"]),
        (DJIA["lastPrice"] - DJIA["previousClose"]),
        (SNP["lastPrice"] - SNP["previousClose"]),
        (FTSE["lastPrice"] - FTSE["previousClose"]),
        (CAC["lastPrice"] - CAC["previousClose"]),
        (NI225["lastPrice"] - NI225["previousClose"]),
        0
    ]

    #Update changes 
    changes = []

    for change_val in change_raw:
        if (change_val == 0):
            changes.append("")
        else:
            changes.append("{0:,.2f}".format(abs(change_val)))

    #Update change symbols
    change_symbols = []

    for change_val in change_raw:
        if (change_val > 0):
            change_symbols.append("▲")
        elif (change_val < 0):
            change_symbols.append("▼")
        else:
            change_symbols.append("")
    

    #Print debug
    debug_headers = ["HSI", "DJIA", "S&P", "FTSE", "CAC", "NI225", "GOLD"]

    print()
    print("Latest Indices:")
    print()
    for i in range(0, 7):
        print(debug_headers[i] + ": ")
        print(prices[i]+" "+change_symbols[i] + changes[i])


    #Update javascript
    
    with open(financeScriptPath, 'r', encoding="utf-8") as file:
        # read a list of lines into data
        data = file.readlines()

        data[0] = "var price = " + str(prices) + "\n"
        data[1] = "var change = " + str(changes)+ "\n"
        data[2] = "var changeSymbol = " + str(change_symbols)+ "\n"

        # and write everything back
        with open(financeScriptPath, 'w', encoding="utf-8") as file:
            file.writelines(data)

    #Write to debug log
    with open(r'.\Debug\MarketPrices-Formatted.txt', 'w', encoding='utf-8') as fp:
        for i in range(0, 7):
            fp.write(debug_headers[i] + ": \n")
            fp.write(prices[i]+" "+change_symbols[i] + changes[i]+"\n\n")