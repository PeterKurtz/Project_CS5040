#!/usr/bin/env python3

# This script downloads the relevant wind speed data over the relevant time span.

from zipfile import ZipFile
import zipfile
from datetime import date, timedelta
import pycurl
import certifi
import logging

START_DATE = date(2013, 8, 15)
END_DATE = date(2014, 5, 1)
# END_DATE = date(2013, 8, 21)

WEBSITE = "https://data.remss.com/ccmp/v03.1"

OUTFILE = "weather.zip"

def date_iter(start, end):
    current = start

    while current != end:
        yield current
        current += timedelta(days=1)

output = ZipFile("weather.zip", "w", compression=zipfile.ZIP_DEFLATED)

curl = pycurl.Curl()

for date in date_iter(START_DATE, END_DATE):
    path = date.strftime("Y%Y/M%m")
    filename = date.strftime("CCMP_Wind_Analysis_%Y%m%d_V03.1_L4.nc")

    url = f"{WEBSITE}/{path}/{filename}"

    with output.open(filename, "w") as f:
        print(f"Writing file {filename}")
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, f)
        curl.setopt(pycurl.CAINFO, certifi.where())
        curl.perform()

output.close()
