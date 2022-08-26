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
from selenium.webdriver.support import expected_conditions as EC

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
settings = config['rakuten']

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

driver.get("https://fes.rakuten-bank.co.jp/MS/main/RbS?CurrentPageID=START&&COMMAND=LOGIN")

driver.execute_script("arguments[0].value = '" + settings["user"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "LOGIN:USER_ID"))))
driver.execute_script("arguments[0].value = '" + settings["pass"] + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "LOGIN:LOGIN_PASSWORD"))))
driver.find_element(By.ID, "LOGIN:_idJsp43").click()
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "HEADER:j_id_vf"))).click()

dt = datetime.now(timezone("Asia/Tokyo"))
start_date = datetime.now() - timedelta(35)
WebDriverWait(driver, 100).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
driver.execute_script("arguments[0].value = '" + start_date.strftime("%Y/%m/%d") + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "FORM_DOWNLOAD_IND:datepicker_from"))))
driver.execute_script("arguments[0].value = '" + dt.strftime("%Y/%m/%d") + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "FORM_DOWNLOAD_IND:datepicker_to"))))

driver.execute_script("validateInquiryTerm = function validateInquiryTerm(downloadType, accountStartDate, term) { if (downloadType === 1) { document.getElementsByClassName('CREDITDEBITINQUIRY_KOJIN_CSV_DOWNLAOD')[0].click(); } else if (downloadType === 2) { document.getElementsByClassName('CREDITDEBITINQUIRY_KOJIN_PDF_DOWNLAOD')[0].click(); } return; } ")

WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "FORM_DOWNLOAD_IND:j_id_68k"))).click()

driver.find_element(By.LINK_TEXT, "デビット利用明細はこちら").click()

driver.execute_script("arguments[0].value = '" + start_date.strftime("%m") + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "FORM_DOWNLOAD:EXPECTED_DATE_FROM_MONTH"))))
driver.execute_script("arguments[0].value = '" + start_date.strftime("%d") + "';", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "FORM_DOWNLOAD:EXPECTED_DATE_FROM_DAY"))))

WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "FORM_DOWNLOAD:_idJsp1385"))).click()

time.sleep(10)
