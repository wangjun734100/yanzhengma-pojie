from selenium import webdriver
url="http://www.ceair.com/"
dirver=webdriver.Chrome()
dirver.get(url)
dirver.maximize_window()