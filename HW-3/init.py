import re
from queue import PriorityQueue
from time import sleep
import urllib
import pickle
from scrapy.linkextractors import IGNORED_EXTENSIONS
from urllib.parse import urlparse, urljoin, urlunparse
from urllib.robotparser import RobotFileParser
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# Recursion limit for pickler if encountered with "ERROR: maximum recursion depth exceeded".
import sys

sys.setrecursionlimit(0x5000)

robot_parse = RobotFileParser()

frontier = PriorityQueue()
frontier.put((1, 1, "http://en.wikipedia.org/wiki/American_Revolutionary_War"))
frontier.put((1, 1, "http://www.history.com/topics/american-revolution/american-revolution-history"))
frontier.put((1, 1, "http://en.wikipedia.org/wiki/American_Revolution"))
frontier.put((1, 1, "http://www.revolutionary-war.net/causes-of-the-american-revolution.html"))


def url_canonicalizer(link_base, link_curr):
    temp_url = urljoin(link_base, link_curr)
    if temp in black_list:
        return -1

    parsed_temp = urlparse(temp_url, allow_fragments=True)
    if parsed_temp.scheme == '' or parsed_temp.netloc in black_list or parsed_temp.netloc == '' \
            or parsed_temp.path.lower().endswith(tuple(IGNORED_EXTENSIONS)):
        return -1
    else:
        scheme = parsed_temp.scheme.lower()
        net = parsed_temp.netloc
        slashes = re.sub(r'//+', '/', parsed_temp.path)
        if net.__contains__(':'):
            if parsed_temp.scheme == "https" and parsed_temp.port == 443:
                net = parsed_temp.hostname
            elif parsed_temp.scheme == "http" and parsed_temp.port == 80:
                net = parsed_temp.hostname
        page = urlunparse(parsed_temp._replace(scheme=scheme, path=slashes, netloc=net.lower(), fragment=''))

        if page in black_list:
            return -1

    return page


def getPriority(url_tuple, in_link):
    count = len(in_link)
    word_count = 0
    if url_tuple[0] is not None:
        for word in url_tuple[0].split():
            for head in key_words:
                if word.lower() in head.split():
                    word_count += 1

    return -(count + word_count)


def add_out_links(wave_curr, url, links):
    out_links = {}
    wave_no = wave_curr + 1
    print("Wave_No for outlinks:", wave_no)
    for i in links:
        if not i['href'].__contains__('#'):
            out_link = url_canonicalizer(url, i['href'])
            if out_link != -1:
                if out_link not in in_links.keys():
                    in_links[out_link] = [url]
                else:
                    in_links[out_link].append(url)

                if out_link not in out_links.keys():
                    out_links[out_link] = [getPriority((i.string, url), in_links[out_link]), url]

    queue_set = set()
    for key in out_links:
        if key not in visited_urls or key not in queue_set:
            frontier.put((wave_no, out_links[key][0], key))
            queue_set.add(key)


def write_info(doc_info, link_dict, file):
    f1 = open("./DATA/Text_Doc/docFile_%s.txt" % file, 'a+')
    for id1 in doc_info:
        f1.write('<DOCID>' + str(id1) + '</DOCID>' + "\n")
        f1.write('<URL>' + doc_info[id1][0] + '</URL>' + "\n")
        f1.write('<HEAD>' + doc_info[id1][1] + '</HEAD>' + "\n")
        f1.write('<TEXT>' + doc_info[id1][2] + '</TEXT>' + "\n\n\n")
    f1.close()

    f2 = open("./DATA/Raw_Doc/rawFile_%s.txt" % file, 'a+')
    for id2 in doc_info:
        f2.write('<DOCID>' + str(id2) + '</DOCID>' + "\n")
        f2.write('<URL>' + doc_info[id2][0] + '</URL>' + "\n")
        f2.write('<HEAD>' + doc_info[id2][1] + '</HEAD>' + "\n")
        f2.write('<RAWHTML>' + doc_info[id2][3] + '</RAWHTML>' + "\n\n\n")
    f2.close()

    ld = open("./DATA/Links_Doc/inlinkFile_%s.txt" % file, 'wb')
    pickle.dump(link_dict, ld)
    ld.close()


visited_urls, key_words = [], ["american", "revolutionary war", "founding fathers", "united states america",
                               "13 colonies", "usa", "benjamin franklin", "revolution", "independence",
                               "george washington", "boston", "tea party", "pennsylvania", "america", "freedom trail"]
hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

black_list = ["http://en.wikipedia.org/wiki/ISBN_(identifier)", "http://en.wikipedia.org/wiki/JSTOR_(identifier)",
              "http://en.wikipedia.org/wiki/Doi_(identifier)", "twitter.com", "https://maven.io/", "books.google.com",
              "amazon.com", "www.facebook.com", "www.instagram.com", "www.wikimedia.com", "www.youtube.com",
              "http://en.wikipedia.org/wiki/ISSN_(identifier)",
              "https://web.archive.org/web/20130508072510/http:/www.history.army.mil/reference/revbib/revwar.htm"]

in_links, doc_dict, temp = {}, {}, {}
url_no, file_no, doc_no = 0, 0, 0
while doc_no <= 40000:
    if not frontier.empty():
        link = frontier.get()[2]
        wave = frontier.get()[0]
        if link not in visited_urls:
            print("Parsing:", link)
            print("Link Count:", doc_no)
            try:
                rob_req = urllib.request.Request(urljoin(link, "/robots.txt"), None, headers=hdr)
                rob_res = urllib.request.urlopen(rob_req, timeout=10)
                robot_parse.parse(rob_res.read().decode("utf-8").splitlines())

                print("Fetch Permission:", robot_parse.can_fetch("*", link))
                print("Sleep Time:", robot_parse.crawl_delay("*"))

                if robot_parse.can_fetch("*", link):
                    if robot_parse.crawl_delay("*") is None:
                        sleep(1)
                    else:
                        sleep(float(robot_parse.crawl_delay("*")))

                    try:
                        req = urllib.request.Request(link, None, hdr)
                        res = urllib.request.urlopen(req, timeout=10)

                        visited_urls.append(link)

                        s = BeautifulSoup(res.read(), "html.parser")

                        # Getting the TITLE
                        title = s.find('title').text
                        # Getting the TEXT
                        Text = ""
                        for txt in s.find_all('p'):
                            Text += txt.text.strip() + "\n"
                        Text = re.sub(r'\[.*\]', '', Text)
                        # Getting the out links
                        link_list = s.find_all('a', href=True)
                        add_out_links(wave, link, list(set(link_list)))

                        url_no += 1
                        doc_no += 1
                        doc_dict[doc_no] = [link, title, Text, s.prettify()]

                        temp[link] = in_links[link]
                        del in_links[link]

                        print("Exited with Code:", res.getcode())

                        # Write to the file.
                        if url_no == 100:
                            file_no += 1
                            write_info(doc_dict, temp, file_no)
                            doc_dict, temp = {}, {}
                            url_no = 0
                            print("================================= PROCESSING DONE =================================")
                    except:
                        visited_urls.append(link)
                        pass
            except:
                visited_urls.append(link)
                pass
