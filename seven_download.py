#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
CSV download
"""

from datetime import datetime, timedelta
from pytz import timezone
import configparser
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
settings = config['seven']

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

driver.get("https://ib.sevenbank.co.jp/IB/IB_U_CO_002/IB_U_CO_002_100.aspx?Lang=ja-JP")

driver.execute_script("arguments[0].value = '" + settings["user"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "cphBizConf_txtLogonId"))))
driver.execute_script("arguments[0].value = '" + settings["pass"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "cphBizConf_txtLogonPw"))))
driver.find_element(By.ID, "cphBizConf_btnLogon").send_keys(Keys.CONTROL + Keys.ENTER)

WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "cphBizConf_lnkMyJCB"))).send_keys(Keys.CONTROL + Keys.ENTER + Keys.ENTER)

driver.switch_to.window(driver.window_handles[1])
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "cphBizConf_btnDebitDetail"))).send_keys(Keys.CONTROL + Keys.ENTER + Keys.ENTER)

driver.switch_to.window(driver.window_handles[2])
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "toDetailsDebitDetailRdc"))).send_keys(Keys.CONTROL + Keys.ENTER)

driver.switch_to.window(driver.window_handles[3])

Select(driver.find_element(By.ID, "seq")).select_by_visible_text('2022年8月16日～2022年9月15日分')
driver.find_element(By.ID, "inquiry").click()
driver.find_element(By.CSS_SELECTOR, "img[src='/apl/myj/common/images/btn-csv-download.jpg']").click()

time.sleep(360)
