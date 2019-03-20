from bs4 import BeautifulSoup
import requests
import json
import csv

url = "https://www.jarir.com/sa-en/catalogsearch/result/?order=priority&dir=asc&q=hp"

re = requests.get(url)

soup = BeautifulSoup(re.text, "lxml")

matches = soup.findAll("h3", {"class": "product-name"})

print "Num of matches: " + str(len(matches))


with open('output.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Model Name", "CPU", "GPU", "Price"])
    for m in matches:
        _title = m.find("a")["title"]
        _title_list = _title.split(",")
        _price = json.loads(m.find("a")["data-layer"])["ecommerce"]["click"]["products"][0]["price"]
        _model_name = _title_list[0]
        _cpu = ""
        _gpu = ""
        for t in _title_list:
            if any(c in t.lower() for c in ["intel", "amd"]):
                _cpu = t
            if any(g in t.lower() for g in ["nvidia"]):
                _gpu = t

        writer.writerow([_title, _cpu, _gpu, _price])
