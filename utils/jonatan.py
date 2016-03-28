# -*- coding: utf-8 -*-
import sys
import os
import requests
import lxml.html
import lxml.etree
import unicodecsv as csv
import urllib

from pprint import PrettyPrinter


URL = "https://paraplan.ru/forum/jonatan.php"
FLIGHT_URL = "https://paraplan.ru/forum/modules.php?name=leonardo&op=show_flight&flightID=45741"


class MyPrettyPrinter(PrettyPrinter):
    def format(self, *args, **kwargs):
        repr, readable, recursive = PrettyPrinter.format(self, *args, **kwargs)
        if repr:
            if repr[0] in ('"', "'"):
                repr = repr.decode('string_escape')
            elif repr[0:2] in ("u'", 'u"'):
                repr = repr.decode('unicode_escape').encode(sys.stdout.encoding)
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


if __name__ == "__main__":
    response = get_page(URL)
    print ("response_status_code = %d " % response.status_code)
    rows = parse_table(response.content)

    # pprint(rows)
    # print (get_igc_url(get_page(FLIGHT_URL).content))

    path = os.path.join(os.path.dirname(__file__), '../examples_jonatan/')

    # opener = urllib.URLopener()
    for row in rows:
        print(row['href'])
        response = get_page(row['href'])
        if response.status_code == 200:
            igc_url = get_igc_url(response.content)
            print(igc_url)
            row['igc_url'] = igc_url
            if(igc_url):
                urllib.urlretrieve("https://paraplan.ru/forum/%s" % igc_url, 
                       filename=os.path.join(path, "%d_%d.igc" % (row['n'], row['flight_number'])))

    with open(os.path.join(path, 'jonatan.csv'), 'w') as fp:
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