#!/usr/bin/python

"""
CoinMarketCap USD Price History
  Print the CoinMarketCap USD price history for a particular cryptocurrency in CSV format.
"""

import sys
import re
import urllib.request
import urllib.error
import pandas as pd

def download_data(currency, start_date, end_date):
  """
  Download HTML price history for the specified cryptocurrency and time range from CoinMarketCap.
  """

  url = 'https://coinmarketcap.com/currencies/' + currency + '/historical-data/' + '?start=' \
                                                + start_date + '&end=' + end_date

  try:
    page = urllib.request.urlopen(url,timeout=10)
    if page.getcode() != 200:
      raise Exception('Failed to load page') 
    html = page.read().decode('utf-8')
    page.close()

  except Exception as e:
    print('Error fetching price data from ' + url)
    print('Did you use a valid CoinMarketCap currency?\nIt should be entered exactly as displayed on CoinMarketCap.com (case-insensitive), with dashes in place of spaces.')
    
    if hasattr(e, 'message'):
      print("Error message: " + e.message)
    else:
      print(e)
      sys.exit(1)

  return html


def extract_data(html):
  """
  Extract the price history from the HTML.
  The CoinMarketCap historical data page has just one HTML table.  This table contains the data we want.
  It's got one header row with the column names.
  We need to derive the "average" price for the provided data.
  """

  head = re.search(r'<thead>(.*)</thead>', html, re.DOTALL).group(1)
  header = re.findall(r'<th .*>([\w /*]+)</th>', head)
  header.append('Average (High + Low / 2)')
  header = [s.replace('*', '') for s in header]

  body = re.search(r'<tbody>(.*)</tbody>', html, re.DOTALL).group(1)
  raw_rows = re.findall(r'<tr[^>]*>' + r'\s*<td[^>]*>([^<]+)</td>'*7 + r'\s*</tr>', body)

  # strip commas
  rows = []
  for row in raw_rows:
    row = [ field.translate(',') for field in row ]
    rows.append(row)

  # calculate averages
  def append_average(row):
    high = float(row[header.index('High')])
    low = float(row[header.index('Low')])
    average = (high + low) / 2
    row.append( '{:.2f}'.format(average) )
    return row
  rows = [ append_average(row) for row in rows ]

  return header, rows


def render_csv_data(header, rows):
  """
  Render the data in CSV format.
  """
  print((','.join(header)))

  for row in rows:
    print((','.join(row)))

# --------------------------------------------- Util Methods -----------------------------------------------------------

def processDataFrame(df):
  import pandas as pd
  assert isinstance(df, pd.DataFrame), "df is not a pandas DataFrame."

  cols = list(df.columns.values)
  cols.remove('Date')
  df.loc[:,'Date'] = pd.to_datetime(df.Date)
  for col in cols: 
    df.loc[:,col] = df[col].apply(lambda x: float(x))
    return df.sort_values(by='Date').reset_index(drop=True)

def rowsFromFile(filename):
    import csv
    with open(filename, 'rb') as infile:
        rows = csv.reader(infile, delimiter=',')
        for row in rows:
            print(row)

# html = download_data(currency, start_date, end_date)
  
#header, rows = extract_data(html) 
#processDataFrame(pd.DataFrame(data=rows,columns=header))
#from datetime import date,timedelta
#current_date=date.today() + timedelta(days=-91)
#x = date.today().strftime('%Y%m%d')
#b = current_date.strftime('%Y%m%d')

