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
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1
})
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get("https://login.paypay-bank.co.jp/wctx/1D1DFxFDg.do")

driver.execute_script("arguments[0].value = '" + settings["tenno"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "idTenNo"))))
driver.execute_script("arguments[0].value = '" + settings["kozano"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "idKozaNo"))))
driver.execute_script("arguments[0].value = '" + settings["pass"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "idPw"))))

driver.find_element(By.ID, "vBtn").click()
time.sleep(12)

driver.find_element(By.NAME, "login").click()
driver.find_element(By.CSS_SELECTOR, "img[src='/commontpl/images/category/welcome_ic003.png']").click()
Select(driver.find_element(By.NAME, "ShokaiStartDateHiIn")).select_by_visible_text('22')
driver.find_element(By.CSS_SELECTOR, ".btn[value='照会']").click()
driver.find_element(By.CSS_SELECTOR, ".btn[value='CSV']").click()
driver.find_element(By.CLASS_NAME, "notWinOpen").click()
Select(driver.find_element(By.NAME, "SyokaiStDate")).select_by_visible_text('22')
driver.find_element(By.CSS_SELECTOR, ".btn[value='照会']").click()
driver.find_element(By.CSS_SELECTOR, ".btn[value='CSV']").click()
time.sleep(10)
