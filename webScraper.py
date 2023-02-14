from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from collections import deque


#########################################################
# 
# Solution tested on both Windows and Linux environments
# on linux, driver got unexpectedly stuck on some runs
# if that happens, moving driver and waiter setup and closing  
# the driver to getTransactionJsonByTXID function should
# fix the issue
# 
#########################################################


# website base url
baseURL = 'https://www.blockchain.com/explorer/transactions/btc/'
# define variables for xpaths
jsonButtonXPath = '/html[1]/body[1]/div[1]/div[2]/div[2]/main[1]/div[1]/div[1]/section[1]/section[1]/div[3]/div[1]/button[2]'
jsonTextXPath = '/html[1]/body[1]/div[1]/div[2]/div[2]/main[1]/div[1]/div[1]/section[1]/section[1]/div[3]/div[2]/div[1]/div[1]/div[1]/pre[1]'

# set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# set waiter and driver timeout
wait = WebDriverWait(driver, 10)
driver.implicitly_wait(10)


# get the transaction JSON from web using Selenium
def getTransactionJsonByTXID(transactionTXID):
    def getTransactionJson():
        try:
            # wait for button to load
            button = wait.until(EC.presence_of_element_located((By.XPATH, jsonButtonXPath)))
            button.click()
            # wait for JSON text to load
            jsonTextElement = wait.until(EC.visibility_of_element_located((By.XPATH, jsonTextXPath)))
            # find json element, extract text and convert to JSON
            return json.loads(jsonTextElement.text), None
        except TimeoutException as err:
            return None, err

    # get the website
    driver.get(baseURL + transactionTXID)
    for _ in range(0,3):
        res, err = getTransactionJson()
        if res != None:
            return res
        driver.refresh()
    raise err


# check if the transaction is coinbase
def isCoinbase(transactionJson):
    return transactionJson['inputs'][0]['coinbase'] == True

# get all inputs TXIDs from transaction JSON
def getINputsTXID(node):
    return [input_node['txid'] for input_node in node.get('inputs', [])]

# BFS implementation
def BFS(startTXID):
    queue = deque([(startTXID, [startTXID])])
    while queue:
        currTXID, currPath = queue.popleft()
        currTransactionJson = getTransactionJsonByTXID(currTXID)
        if isCoinbase(currTransactionJson):
            return currPath
        for neighborTXID in getINputsTXID(currTransactionJson):
            queue.append((neighborTXID, currPath + [neighborTXID]))
    return []


def main():
    startTXID = '79ec6ef52c0a2468787a5f671f666cf122f68aaed11a28b15b5da55c851aee75'
    res = BFS(startTXID)
    # print results
    for elem in res:
        print(elem)
    driver.close()

main()