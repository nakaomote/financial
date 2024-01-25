#!/bin/bash

set -eux
set -o pipefail

## TODO:
## - Make transaction IDs link to date.
##   - This should avoid a lot of issues.
##   - Need to make sure if items change...

# ANA suica visa credit card.
#./vpass.py 202???.csv 74,692 6 | tee vpass.csv

# UFJ
#./ufj_download.py
#./ufj.py 0019642_*.csv | tee ufj.csv

# Seven Eleven Bank.
#./seven_download.py
#./seven.py *_debitmeisai.csv | tee seven.csv

# Mobile pasumo
# TODO: Add in a selenium portion that'll download the html.
# TODO: Make the selenium ask about the capture.
#./mobilePasumo.py | tee mobile.csv

# PayPay bank
#./jnb_download.py
#./jnb.py NB*.csv > jnb.csv
#./jnb.py shiftjis/* | tee jnb.csv

# A's pasumo.
#mv ~/ダウンロード/01010a107b19ba0e_* ./
#./pasumo.py 01010a107b19ba0e_* > ~/work/financial/pasumo-a.csv

# Our Sony accounts.
for user in $(awk -F '[_\\]]' ' /sony_/ { print $2 } ' config.ini); do
    ./sony_download.py "${user}"
    ./sony.py ./YenFutsuRireki.csv 2021-03-23 | tee "sony_${user}.csv"
done

# Rakuten.
#./rakuten_download.py
#./rakuten.py RB-debitmeisai.csv RB-torihikimeisai.csv > rakuten.csv

# Mobile pasumo
# TODO: Add in a selenium portion that'll download the html.
# TODO: Make the selenium ask about the capture.
#./mobilePasumo.py | tee mobile.csv
