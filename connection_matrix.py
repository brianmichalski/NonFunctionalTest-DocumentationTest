# Question 4

import bs4 as bs
import urllib.request as request
import re
import csv
import os
from urllib.error import HTTPError, URLError

def extractLinks(base_url, current_page, visited_links):
    print_msg = f"Processing page {current_page}..."
    print(print_msg, " " * (100 - len(print_msg)), end="\r"),

    soup = None
    full_url = base_url + current_page
    try:
        source = request.urlopen(full_url).read()
        soup = bs.BeautifulSoup(source, "lxml")
    except (HTTPError, URLError) as error:
        # print(f"Failed to fetch {full_url}: {error}")
        return False

    links = soup.find_all("a")
    # regex filter for capturing all pages in the first level of the site
    # it avoids javascript() links, inner refs (#), external links, etc.
    regex = r"(?:https:\/\/www\.linux-kvm\.org\/)?page((\/[\w+\-]+){1,})"
    m = ""
    new_pages = []
    for link in links:
        # if the link there's no target page, ignore
        if link.get("href") == None:
            continue

        m = re.search(regex, link.get("href"))
        # if the link matches the regex, store it as selected
        if m != None:
            new_page = m.group(1)
            visited_links[current_page].add(new_page)
            if new_page in visited_links:
                continue

            visited_links[new_page] = set()
            new_pages.append(new_page)

            # Sleep to avoid making too many requests quickly
            # time.sleep(1)

    for page in new_pages:
        extractLinks(base_url, page, visited_links)

    return True


base_url = "https://www.linux-kvm.org/page"
visited_links = {}
main_page = "/Main_Page"
visited_links[main_page] = set()

extractLinks(base_url, main_page, visited_links)
print(" " * 100, end="\r"),

row = None

csv_output_file = "connection_matrix.csv"
# check whether the file exists
if os.path.exists(csv_output_file):
    # delete the file
    os.remove(csv_output_file)
    
with open(csv_output_file, "w", newline="") as csvfile:
    csv_writer = csv.writer(
        csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
    )

    header = [""]
    for col in visited_links.keys():
        header.append(col)
    csv_writer.writerow(header)

    for rowPage, rowLinks in visited_links.items():
        row = [rowPage]
        for colPage, colLinks in visited_links.items():
            row.append(1 if colPage in rowLinks else 0)

        csv_writer.writerow(row)
