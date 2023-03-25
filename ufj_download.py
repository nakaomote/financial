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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
settings = config['ufj']

options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--remote-debugging-port=4444")
options.add_experimental_option("prefs", {
    "download.default_directory": os.path.join(os.environ["HOME"], "work/financial"),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://entry11.bk.mufg.jp/ibg/dfw/APLIN/loginib/login?_TRANID=AG004_001")

driver.execute_script("arguments[0].value = '" + settings["keiyakuno"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "tx-contract-number"))))
driver.execute_script("arguments[0].value = '" + settings["pass"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "tx-ib-password"))))

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "gonext")))
driver.find_element(By.CLASS_NAME, "gonext").click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "detail")))
driver.find_element(By.CLASS_NAME, "detail").click()
driver.implicitly_wait(10)

driver.find_element(By.CSS_SELECTOR, "img[src='https://directg.s.bk.mufg.jp/refresh/imgs/_DIRECT_IMAGE/YEN/btn_meisai_download_off.gif']").click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "appoint")))
driver.find_element(By.ID, "appoint").click()
driver.find_element(By.CSS_SELECTOR, "img[src='https://directg.s.bk.mufg.jp/refresh/imgs/_DIRECT_IMAGE/COMMON/btn_download_off.jpg']").click()
time.sleep(10)
