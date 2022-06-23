#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
CSV download
"""

import configparser
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
settings = config['jnb']

options = Options()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument('--disable-dev-shm-usage')
# XXX TODO
#options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--remote-debugging-port=4444")
options.add_experimental_option("prefs", {
    "download.default_directory": "/home/william.fletcher/work/financial",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get("https://login.paypay-bank.co.jp/wctx/1D1DFxFDg.do")
driver.find_element_by_id("idTenNo").send_keys(settings["tenno"])
driver.find_element_by_id("idKozaNo").send_keys(settings["kozano"])
# XXX TODO: Send the password.
# XXX kpcli --kdb ~/work/passwords --pwfile ~/crypt/master_password -c 'show banks/jnb -f' 
driver.find_element_by_id("vBtn").click()
time.sleep(12)

driver.find_element_by_name("login").click()
driver.find_element_by_css_selector("img[src='/commontpl/images/category/welcome_ic003.png']").click()
Select(driver.find_element_by_name("ShokaiStartDateHiIn")).select_by_visible_text('22')
driver.find_element_by_css_selector(".btn[value='照会']").click()
driver.find_element_by_css_selector(".btn[value='CSV']").click()
driver.find_element_by_class_name("notWinOpen").click()
Select(driver.find_element_by_name("SyokaiStDate")).select_by_visible_text('22')
driver.find_element_by_css_selector(".btn[value='照会']").click()
driver.find_element_by_css_selector(".btn[value='CSV']").click()
time.sleep(10)
