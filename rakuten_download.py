#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
CSV download
"""

import requests

session = requests.Session()
session.get("https://fes.rakuten-bank.co.jp/MS/main/RbS?CurrentPageID=START&&COMMAND=LOGIN")

post = {
    "LOGIN_SUBMIT": "1",
    "jsf_sequence": "1",
    "LOGIN:_link_hidden_": "LOGIN:_idJsp43",
    "LOGIN:LOGIN_PASSWORD_CHECK": "TOOLTIP_CHECK",
    "LOGIN:USER_ID": "YOURUSER",
    "LOGIN:LOGIN_PASSWORD": "YOURPASS"
}

session.post("https://fes.rakuten-bank.co.jp/MS/main/fcs/rb/fes/jsp/mainservice/Security/LoginAuthentication/Login/Login.jsp", post)
session.get("https://fes.rakuten-bank.co.jp/MS/main/gns?COMMAND=BALANCE_INQUIRY_START&=&CurrentPageID=HEADER_FOOTER_LINK")
session.get("https://fes.rakuten-bank.co.jp/MS/main/gns?COMMAND=CREDIT_DEBIT_INQUIRY_START&&CurrentPageID=HEADER_FOOTER_LINK")

post = {
    "FORM_DOWNLOAD_IND:datepicker_from": '2021/11/23',
    "FORM_DOWNLOAD_IND:datepicker_to": '2022/01/25',
    "FORM_DOWNLOAD_IND:ACCOUNTOPEN_DATE": '2014/09/04',
    "FORM_DOWNLOAD_IND:DOWNLOAD_TYPE": '0',
    "FORM_DOWNLOAD_IND_SUBMIT": '1',
    "FORM_DOWNLOAD_IND:_link_hidden_": 'FORM_DOWNLOAD_IND:_idJsp695'
}

r = session.post("https://fes.rakuten-bank.co.jp/MS/main/fcs/rb/fes/jsp/mainservice/Inquiry/CreditDebitInquiry/CreditDebitInquiry/CreditDebitInquiry.jsp", data=post)
with open("rakuten_bank.csv", "w") as rb:
    rb.write(r.text)

session.get("https://fes.rakuten-bank.co.jp/MS/main/gns?COMMAND=BALANCE_INQUIRY_START&=&CurrentPageID=HEADER_FOOTER_LINK")
session.get("https://fes.rakuten-bank.co.jp/MS/main/gns?COMMAND=CREDIT_DEBIT_INQUIRY_START&&CurrentPageID=HEADER_FOOTER_LINK")

post = {
    "FORM_CONFIRM_SUBMIT": "1",
    "FORM_CONFIRM:_link_hidden_": "FORM_CONFIRM:_idJsp194",
}
r = session.post("https://fes.rakuten-bank.co.jp/MS/main/fcs/rb/fes/jsp/mainservice/Inquiry/CreditDebitInquiry/CreditDebitInquiry/CreditDebitInquiry.jsp", data=post)

post = {
        "FORM_DOWNLOAD:EXPECTED_DATE_FROM_YEAR": "2021",
        "FORM_DOWNLOAD:EXPECTED_DATE_FROM_MONTH": "10",
        "FORM_DOWNLOAD:EXPECTED_DATE_FROM_DAY": "27",
        "FORM_DOWNLOAD:EXPECTED_DATE_TO_YEAR": "2022",
        "FORM_DOWNLOAD:EXPECTED_DATE_TO_MONTH": "01",
        "FORM_DOWNLOAD:EXPECTED_DATE_TO_DAY": "25",
        "FORM_DOWNLOAD:transitionSourceFlag": "",
        "FORM_DOWNLOAD_SUBMIT": "1",
        "FORM_DOWNLOAD:_link_hidden_": "FORM_DOWNLOAD:_idJsp1385"
}

r = session.post("https://fes.rakuten-bank.co.jp/MS/main/fcs/rb/fes/jsp/mainservice/CardManagement/DebitList/DebitList/DebitList.jsp", data=post)
r = print(r.text)
