# -*- coding: utf-8 -*-
import sys
import os

import multiprocessing
import time

import requests
import lxml.html
import lxml.etree
import unicodecsv as csv
import urllib
import codecs

from pprint import PrettyPrinter


URL = "https://paraplan.ru/forum/jonatan.php"
FLIGHT_URL = "https://paraplan.ru/forum/modules.php?name=leonardo&op=show_flight&flightID=45741"

class MyPrettyPrinter(PrettyPrinter):
    def format(self, *args, **kwargs):
        repr, readable, recursive = PrettyPrinter.format(self, *args, **kwargs)
        if repr:
            if repr[0] in ('"', "'"):
                repr = str(codecs.escape_decode(repr))
            elif repr[0:2] in ("u'", 'u"'):
                repr = str(codecs.decode(repr, 'unicode_escape').encode(sys.stdout.encoding))
        return repr, readable, recursive


def pprint(obj, stream=None, indent=1, width=80, depth=None):
    printer = MyPrettyPrinter(stream=stream, indent=indent, width=width, depth=depth)
    printer.pprint(obj)


def get_page(url=URL):
    resp = requests.get(url)
    return resp


def parse_table(content):
    html = lxml.html.fromstring(content)
    trs = html.xpath('//table/tr')[2:]
    if trs:
        del trs[-1]

    rows = []
    for tr in trs:
        r = {}

        # cells = tr.xpath('.//td//text()')
        tds = tr.getchildren()
        cells = [td.xpath("string()") for td in tds]

        # pprint (cells)
        if cells:
            [n, name] = cells[0].split('.')
            r = dict(
                n=int(n),
                name=name,
                nickname=cells[1],
                command=cells[2],
                flight_number=int(cells[3]),
                dt=cells[4].split()[0],
                start=cells[5],
                glider=cells[-4],
                task=cells[-3],
                points=float(cells[-2]),
                href=tr.xpath('.//a//@href')[0],
            )
            # pprint(r)
            rows.append(r)
    return rows


def get_igc_url(content):
    html = lxml.html.fromstring(content)
    href = html.xpath('//a[text()="IGC"]/@href')
    href = href[0] if len(href)>0 else None
    return href


def get_igc(row):
    # lock.acquire()
    href = row['href']
    print(href)
    time.sleep(10)
    # lock.release()

    resp = get_page(row['href'])
    igc_url = None
    if resp.status_code == 200:
        igc_url = get_igc_url(resp.content)
        print(igc_url)
        if (igc_url):
            url = "https://paraplan.ru/forum/{}".format(igc_url)
            path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../examples_jonatan/'))

            name = os.path.join(path, "{}_{}.igc".format(row['n'], row['flight_number']))
            print(f"URL: {url} \nname:{name}\n")
            urllib.request.urlretrieve(url, name)

    else:
        print('Error: {:d}'.format(resp.status_code))
    return {'igc_url': igc_url}


if __name__ == "__main__":
    response = get_page(URL)
    print ("response_status_code = {}".format(response.status_code))
    rows = parse_table(response.content)

    # pprint(rows)
    # print (get_igc_url(get_page(FLIGHT_URL).content))

    path = os.path.join(os.path.dirname(__file__), '../examples_jonatan/')

    PROCESSES = 1
    pool = multiprocessing.Pool(PROCESSES)
    res = [pool.apply_async(get_igc, [row], callback=row.update) for row in rows]
    pool.close()
    pool.join()

    with open(os.path.join(path, 'jonatan.csv'), 'wb') as fp:
        writer = csv.DictWriter(fp, delimiter=",",
        fieldnames=[
            'n',
            'flight_number',
            'name',
            'nickname',
            'points',
            'task',
            'start',
            'dt',
            'href',
            'command',
            'glider',
            'igc_url'
        ])
        for row in rows:
            writer.writerow(row)

    pprint(rows)