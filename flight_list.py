#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawl web page for building csv files containing flights info
 
Usage:
  flight_list.py <company> [--from=<from> --to=<to>]
 
Options:
  -h --help     
  --version
  # -company=TODO
  # --from=TODO    
  # --to=TODO   
"""
import os
import re
import sys
import urllib2
from bs4 import BeautifulSoup
from docopt import docopt

separator = ";"
url = "http://www.flightradar24.com/data/flights/"
# company = "air-france-afr"
# directory = company
_from = 0;
_to = 10

# remove annoying characters
chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xcc\xb1' : ''          # modifier - under line
}

def replace_chars(match):
    char = match.group(0)
    return chars[char]

def replace(text):
    return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, text)

def parseRow(row):
    cells = row.find_all('td')
    date = row.get('data-date')
    fromAirPort = row.get('data-name-from')
    toAirPort = row.get('data-name-to')
    aircraft = cells[3].contents[0].encode('utf-8')
    std = cells[4].contents[0].encode('utf-8')
    atd = cells[5].contents[0].encode('utf-8')
    sta = cells[6].contents[0].encode('utf-8')
    status = cells[7].contents[1].encode('utf-8')
    statusStrong = cells[7].find('strong')
    if statusStrong:
        status = statusStrong.contents[0].encode('utf-8')

    return [date, fromAirPort, toAirPort, replace(aircraft), std, atd, sta, replace(status)]

def parseTable(data_flight, idTable):
    response = urllib2.urlopen(url + data_flight + "/") #may have some issues
    page_source = response.read()
    soup = BeautifulSoup(page_source)
    table = soup.find_all('table')
    
    result = []
    
    if table and len(table) >= 1:
        table = table[0]
        headers = table.find_all("th")
        if headers:
            headers_list = []
            for i in range(0,8):
                headerName = headers[i].string
                if headerName:
                    headers_list.append(headerName)

            assert len(headers_list) == 8 #simple check
            result.append(headers_list)

        rows = table.tbody.find_all('tr')
        for row in rows:
            try:
                result.append(parseRow(row))
            except:
                print "Flight: #" + data_flight + " -- Unexpected error:", sys.exc_info()[0]

    return result

def writeInCsvFile(list_of_flights):
    for flight in list_of_flights:
        fileName = directory + "/" + flight + ".csv"
        with open(fileName, "w+") as f:
            matrix = parseTable(flight, "tblFlightData")
            for row in matrix:
                try:
                    f.write(separator.join(row))
                except:
                    print "Flight: #" + flight + " -- Unexpected error:", sys.exc_info()[0]
                f.write('\n')
            f.close()
        print fileName + " created"

if __name__ == '__main__':
    # __doc__ contient automatiquement la docstring du module
    # en cours
    arguments = docopt(__doc__, version='0.1')
    if arguments['<company>']:
        print "Starting ..."
        company = arguments['<company>']
        directory = company

        if arguments['--from']:
            _from = int(arguments['--from'])
        if arguments['--to']:
            _to = int(arguments['--to'])

        response = urllib2.urlopen(url + company)
        page_source = response.read()
        soup = BeautifulSoup(page_source)
        li_tab = soup.find_all('li')

        list_of_flights = []
        for li_elem in li_tab:
          data_flight = li_elem.get("data-flight")
          if data_flight:
              list_of_flights.append(data_flight)

        if not os.path.exists(directory):
          os.makedirs(directory)

        writeInCsvFile(list_of_flights[_from:_to])

        print "... finished !"
    else:
        print arguments
