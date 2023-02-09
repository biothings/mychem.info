#!/bin/bash

export apikey=$1
export DOWNLOAD_URL=$2

export CAS_LOGIN_URL=https://utslogin.nlm.nih.gov/cas/v1/api-key


if [ $# -eq 0 ]; then echo "Usage: download.sh apikey download_url"
                      echo "  e.g. download.sh e33c59db-1234-abcd-efgh-0117ab2cd5gh2  https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_full_current.zip"
                      echo "       download.sh e33c59db-1234-abcd-efgh-0117ab2cd5gh2 https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_weekly_current.zip"
   exit
fi


if [ -z "$apikey" ]; then echo " Please enter you api key "
   exit
fi

if [ -z "$DOWNLOAD_URL" ]; then echo " Please enter the download_url "
   exit
fi


TGT=$(curl -d "apikey="$apikey -H "Content-Type: application/x-www-form-urlencoded" -X POST https://utslogin.nlm.nih.gov/cas/v1/api-key)

TGTTICKET=$(echo $TGT | tr "=" "\n")

for TICKET in $TGTTICKET
do
    if [[ "$TICKET" == *"TGT"* ]]; then
      SUBSTRING=$(echo $TICKET| cut -d'/' -f 7)
      TGTVALUE=$(echo $SUBSTRING | sed 's/.$//')
    fi
done
echo $TGTVALUE
STTICKET=$(curl -d "service="$DOWNLOAD_URL -H "Content-Type: application/x-www-form-urlencoded" -X POST https://utslogin.nlm.nih.gov/cas/v1/tickets/$TGTVALUE)
echo $STTICKET

curl -c cookie.txt -b cookie.txt -L -O -J $DOWNLOAD_URL?ticket=$STTICKET
rm cookie.txt