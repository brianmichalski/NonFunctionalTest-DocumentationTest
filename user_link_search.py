# Question 5

import bs4 as bs
import urllib.request as request
import re
from thefuzz import process, fuzz
from urllib.error import HTTPError, URLError

def searchLink(links, query):
    search_result = process.extract(query, links, scorer=fuzz.ratio)
    for value in search_result:
        print(value)
        
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
            if new_page in visited_links:
                continue

            visited_links[new_page] = link.text
            new_pages.append(new_page)

            # Sleep to avoid making too many requests quickly
            # time.sleep(1)

    for page in new_pages:
        extractLinks(base_url, page, visited_links)

    return True


base_url = "https://www.linux-kvm.org/page"
visited_links = {}
main_page = "/Main_Page"
visited_links[main_page] = 'Home'

extractLinks(base_url, main_page, visited_links)
print(" " * 100, end="\r"),

links_swap = {v: k for k, v in visited_links.items()}

while True:
    search_input = input("Enter your query (or press Enter to stop): ")
    if search_input == "":
        break
    
    print(f"Results for '{search_input}'")
    searchLink(visited_links, search_input)
    print('\n'*2)