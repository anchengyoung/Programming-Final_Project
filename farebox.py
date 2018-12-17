import wikipedia, re
from BeautifulSoup import BeautifulSoup

def get_data():
    wiki_search_string = "Farebox recovery ratio"
    wiki_page_title = "Farebox recovery ratio"
    wiki_table_caption = "Ratio of fares to operating costs for public transport systems"
    parsed_table_data = []

    search_results = wikipedia.search(wiki_search_string)
    for result in search_results:
        if wiki_page_title in result:
            my_page = wikipedia.page(result)
            soup = BeautifulSoup(my_page.html())
            table = soup.find('caption',text=re.compile(r'%s'%wiki_table_caption)).findParent('table')
            rows = table.findAll('tr')
            for row in rows:
                children = row.findChildren(recursive=False)
                row_text = []
                for child in children:
                    clean_text = child.text
                    clean_text = clean_text.split('&#91;')[0]
                    clean_text = clean_text.split('&#160;')[-1]
                    clean_text = clean_text.strip()
                    row_text.append(clean_text)
                parsed_table_data.append(row_text)
    return parsed_table_data

continent = []
country = []
system = []
ratio = []
raw_fare_system = []
raw_fare = []
year = []

if __name__=="__main__":
    clean_data = get_data()[1:]
    for row in clean_data:
        continent.append(row[0])
        country.append(row[1])
        system.append(row[2])
        ratio.append(float((row[3].split("%"))[0]))
        raw_fare_system.append(row[4])
        raw_fare.append(row[5])
        year.append(int((row[6].split("/"))[0]))

def CleanFare(raw_fare):
    if "+ (Bus)" in raw_fare:
        return raw_fare.split("+")[0]
    if "(Bus)" in raw_fare:
        return raw_fare.split("(Bus)")[0]
    if "+" in raw_fare:
        return raw_fare.split("+")[0]
    if "-" in raw_fare:
        return raw_fare.split("-")[0]
    if "From" in raw_fare:
        return re.split("m| /", raw_fare)[1]
    if "cash" in raw_fare:
        return raw_fare.split(" (")[0]
    if " /" in raw_fare:
        return raw_fare.split(" /")[0]
    if " (" in raw_fare:
        return raw_fare.split(" (")[0]
    if "," in raw_fare:
        return raw_fare.split(",")[0]
    if "to" in raw_fare:
        return raw_fare.split("to")[0]
    else:
        return raw_fare

fare_rate = []
for x in raw_fare:
    fare_rate.append(CleanFare(x))

from forex_python.converter import CurrencyRates
import twder

c = CurrencyRates()

def Converter(fare_rate):
    if "EUR" in fare_rate:
        return round((c.get_rate('EUR','USD'))*float(fare_rate.split("EUR")[1]), 2)
    if u'\u20ac' in fare_rate:
        return round((c.get_rate('EUR','USD'))*float(fare_rate.split(u'\u20ac')[1]), 2)
    if u'\xa5' in fare_rate:
        return round((c.get_rate('JPY','USD'))*float(fare_rate.split(u'\xa5')[1]), 2)
    if "HK$" in fare_rate:
        return round((c.get_rate('HKD','USD'))*float(fare_rate.split("HK$")[1]), 2)
    if "SEK" in fare_rate:
        return round((c.get_rate('SEK','USD'))*float(fare_rate.split("SEK")[1]), 2)
    if "SGD" in fare_rate:
        return round((c.get_rate('SGD','USD'))*float(fare_rate.split("SGD")[1]), 2)
    if "CZK" in fare_rate:
        return round((c.get_rate('CZK','USD'))*float(fare_rate.split("CZK")[1]), 2)
    if "CNY" in fare_rate:
        return round((c.get_rate('CNY','USD'))*float(fare_rate.split("CNY")[1]), 2)
    if "C$" in fare_rate:
        return round((c.get_rate('CAD','USD'))*float(fare_rate.split("C$")[1]), 2)
    if "A$" in fare_rate:
        return round((c.get_rate('AUD','USD'))*float(fare_rate.split("A$")[1]), 2)
    if "CHF" in fare_rate:
        return round((c.get_rate('CHF','USD'))*float(fare_rate.split("CHF")[1]), 2)
    if "NT$" in fare_rate:
        return round((float(fare_rate.split("NT$")[1])/float(twder.now('USD')[1])), 2)
    if "PKR" in fare_rate:
        return round((float(fare_rate.split("PKR")[1])/139.10), 2)
    if "US$" in fare_rate:
        return float(fare_rate.split("US$")[1])
    else:
        return "NA"

us_rate = []
for x in fare_rate:
    us_rate.append(Converter(x))

def CleanSystem(raw_fare_system):
    if "Zone" in raw_fare_system:
        return "Zone based"
    if "Flat" in raw_fare_system:
        return "Flat rate"
    if "Distance" in raw_fare_system:
        return "Distance based"
    else:
        return "Other"

fare_system = []
for x in raw_fare_system:
    fare_system.append(CleanSystem(x))


import sqlite3

db_file = "farebox.db"
conn = sqlite3.connect(db_file)

create_table_sql = """CREATE TABLE IF NOT EXISTS farebox_ratio(
                                                continent TEXT,
                                                country TEXT,
                                                system TEXT,
                                                ratio REAL,
                                                fare_system TEXT,
                                                fare_rate TEXT,
                                                us_rate REAL,
                                                year REAL
                                                );"""

cur=conn.cursor()
cur.execute(create_table_sql)

for a, b, c, d, e, f, g, h in zip(continent, country, system, ratio, fare_system, fare_rate, us_rate, year):
    sql = """INSERT INTO farebox_ratio(continent, country, system,
                                        ratio, fare_system, fare_rate,
                                        us_rate, year) VALUES ('%s', '%s',
                                        '%s', '%s', '%s', '%s', '%s', '%s');""" %(a, b, c, d, e, f, g, h)
    cur.execute(sql)
    conn.commit()
