#!/bin/bash

set -eux
set -o pipefail

## TODO:
## - Make transaction IDs link to date.
##   - This should avoid a lot of issues.
##   - Need to make sure if items change...

## TODO: automate this freaking login.
# ANA suica visa credit card.
#mv -v ~/ダウンロード/202???.csv ./
#./vpass.py 202???.csv "${1}" 6 | tee vpass.csv

# PayPay bank
#./jnb_download.py
##./jnb.py 2024 8 1 NB*.csv | tee jnb.csv
##./jnb.py shiftjis/* | tee jnb.csv

# A's pasumo.
#mv ~/ダウンロード/01010a107b19ba0e_* ./
#./pasumo.py 01010a107b19ba0e_* > ~/work/financial/pasumo-a.csv
#
# W's pasumo.
#mv ~/ダウンロード/01010a109c15d217_* ./
#./pasumo.py 01010a109c15d217_* > ~/work/financial/pasumo-w.csv

# Mobile pasumo
# arg: day of month.
#./mobilePasumo.py ${1:-} | tee mobile.csv

# Olive bank account.
#mv -v /home/ultraviolet/ダウンロード/meisai*.csv ./
#./olive.py meisai*.csv | tee olive.csv
