#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
CSV download
"""

import requests
import configparser
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
settings = config['ufj']

options = Options()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--remote-debugging-port=4444")
options.add_experimental_option("prefs", {
    "download.default_directory": "/home/william.fletcher/work/financial",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get("https://entry11.bk.mufg.jp/ibg/dfw/APLIN/loginib/login?_TRANID=AG004_001")
driver.find_element_by_id("tx-contract-number").send_keys(settings["keiyakuno"])
driver.find_element_by_id("tx-ib-password").send_keys(settings["pass"])
driver.find_element_by_class_name("gonext").click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "detail")))
driver.find_element_by_class_name("detail").click()
driver.implicitly_wait(10)
driver.find_element_by_css_selector("img[src='https://directg.s.bk.mufg.jp/refresh/imgs/_DIRECT_IMAGE/YEN/btn_meisai_download_off.gif']").click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "appoint")))
driver.find_element_by_id("appoint").click()
driver.find_element_by_css_selector("img[src='https://directg.s.bk.mufg.jp/refresh/imgs/_DIRECT_IMAGE/COMMON/btn_download_off.jpg']").click()
time.sleep(10)