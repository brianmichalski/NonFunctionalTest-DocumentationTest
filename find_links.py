# Question 3

import bs4 as bs
import urllib.request as request
import re
from urllib.error import HTTPError, URLError
from collections import defaultdict

class PrintTree:
    def printTree(self, tree, d=0):
        if tree == None or len(tree) == 0:
            return
        else:
            for key, val in tree.items():
                if val == None:
                    continue
                if isinstance(val, dict):
                    print("\t" * d, key)
                    self.printTree(val, d + 1)
                else:
                    print("\t" * d, key, f'({val})')


def extractPageTree(base_url, current_page, tree_node, visited_links):
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
    regex = r"^\/page((\/[\w+]+){1,})"
    m = ""
    new_pages = []
    for current_page in links:
        # if the link there's no target page, ignore
        if current_page.get("href") == None:
            continue

        m = re.search(regex, current_page.get("href"))
        # if the link matches the regex, store it as selected
        if m != None:
            new_page = m.group(1)
            if new_page in visited_links:
                continue

            visited_links[new_page] = m.group(2)
            new_pages.append(new_page)

            # Sleep to avoid making too many requests quickly
            # time.sleep(1)

    for page in new_pages:
        if page in tree_node:
            continue

        tree_node[page] = defaultdict()
        if not extractPageTree(base_url, page, tree_node[page], visited_links):
            tree_node[page] = '!404'
            
    return True


base_url = "https://www.linux-kvm.org/page"
visited_links = {}
main_page = "/Main_Page"
visited_links[main_page] = "Main"
main_node = defaultdict()

extractPageTree(base_url, main_page, main_node, visited_links)
print(" " * 100, end="\r"),

# uncomment the following lines to see the output as a list

# sorted_links = sorted(visited_links.items())
# for key, value in sorted_links:
#     print(key, '=>', value)


# print the output as a tree
printer = PrintTree()
printer.printTree(main_node)
