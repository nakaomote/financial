#!/bin/bash

set -eux
set -o pipefail

## TODO:
## - Make transaction IDs link to date.
##   - This should avoid a lot of issues.
##   - Need to make sure if items change...
#

## TODO: automate this freaking login.
# ANA suica visa credit card.
#mv -v ~/ダウンロード/202???.csv ./
#./vpass.py 202???.csv 10,421 6 | tee vpass.csv

# UFJ
#./ufj_download.py
#./ufj.py 0019642_*.csv | tee ufj.csv

# Seven Eleven Bank.
#./seven_download.py
#./seven.py *_debitmeisai.csv | tee seven.csv

# PayPay bank
#./jnb_download.py
#./jnb.py 2024 6 1 NB*.csv | tee jnb.csv
#./jnb.py shiftjis/* | tee jnb.csv

# A's pasumo.
#mv ~/ダウンロード/01010a107b19ba0e_* ./
#./pasumo.py 01010a107b19ba0e_* > ~/work/financial/pasumo-a.csv
#
# Our Sony accounts.
#for user in $(awk -F '[_\\]]' ' /sony_/ { print $2 } ' config.ini); do
#    ./sony_download.py "${user}"
#    ./sony.py ./YenFutsuRireki.csv 2021-03-23 | tee "sony_${user}.csv"
#done

# Rakuten.
#./rakuten_download.py
#./rakuten.py RB-debitmeisai.csv RB-torihikimeisai.csv > rakuten.csv

# Mobile pasumo
#./mobilePasumo.py
#./mobilePasumo.py | tee mobile.csv
#./mobilePasumo.py 02 | tee mobile.csv

# Olive bank account.
# ./olive.py meisai\ \(4\).csv | tee olive.csv
