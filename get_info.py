import csv
import time
import requests
import json

from bs4 import BeautifulSoup
from flask import Flask, stream_with_context, request
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
from cStringIO import StringIO

app = Flask(__name__)


def get_laptop_info_by_brand(brand):
    page = 1
    result_list = []

    while True:
        url = "https://www.jarir.com/sa-en/catalogsearch/result/?order=priority&dir=asc&q=" + str(brand) + \
              "+laptop&p=" + str(page) + "&is_scroll=1"
        re = requests.get(url)
        soup = BeautifulSoup(re.text, "lxml")
        matches = soup.findAll("h3", {"class": "product-name"})

        for m in matches:
            _title = m.find("a")["title"]
            _title_list = _title.split(",")
            _price = json.loads(m.find("a")["data-layer"])["ecommerce"]["click"]["products"][0]["price"]
            _model_name = _title_list[0]
            _cpu = ""
            _gpu = ""
            _cpu_count = 0
            for t in _title_list:
                if any(c in t.lower() for c in ["intel", "amd"]) and _cpu_count is 0:
                    _cpu = t
                    _cpu_count = _cpu_count + 1
                elif any(g in t.lower() for g in ["nvidia", "amd", "intel"]):
                    _gpu = t

            result_list.append([_title, _cpu, _gpu, _price])
        # print len(matches)

        if len(matches) < 20:
            return result_list
        else:
            page += 1
            time.sleep(1)


@app.route("/")
def hello():
    brand_list = request.args.getlist("brand")
    result_list = []

    for brand in brand_list:
        result_list.extend(get_laptop_info_by_brand(brand))

    return str(result_list)


@app.route("/file")
def download_info():
    def generate():
        brand_list = request.args.getlist("brand")
        result_list = []

        for brand in brand_list:
            result_list.extend(get_laptop_info_by_brand(brand))

        data = StringIO()
        w = csv.writer(data)

        # write header
        w.writerow(("Model Name", "CPU", "GPU", "PRICE"))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # write each log item
        for r in result_list:
            w.writerow(r)
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    # add a filename
    headers = Headers()
    headers.set('Content-Disposition', 'attachment', filename='laptop-info.csv')

    # stream the response as the data is generated
    return Response(
        stream_with_context(generate()),
        mimetype='text/csv', headers=headers
    )


if __name__ == "__main__":
    app.run()
