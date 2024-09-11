import csv
import re
import logging
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_html(url):
    """Fetches the HTML content of the provided URL."""
    try:
        return urlopen(url)
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None


def get_all_pages_links(base_url):
    """Gets all page links for the A-to-Z directory."""
    html = fetch_html(base_url)
    if not html:
        return []

    bs = BeautifulSoup(html, 'lxml')
    all_pages_link_tags = bs.find_all('a', href=re.compile(
        r'^/discover-charities/a-to-z-directory/charities-starting-with-[a-z].html'))
    all_pages_links = [f"https://www.charitynavigator.org{tag['href']}" for tag in all_pages_link_tags]
    all_pages_links.insert(0, base_url)  # Insert the base URL
    logging.info(f"Found {len(all_pages_links)} page links.")
    return all_pages_links


def get_charity_links(page_link):
    """Extracts charity EIN links from a page."""
    html = fetch_html(page_link)
    if not html:
        return []

    bs = BeautifulSoup(html, 'lxml')
    link_tags = bs.find_all('a', href=re.compile('https://www.charitynavigator.org/ein/[0-9]+$'))
    links = [tag['href'] for tag in link_tags]
    logging.info(f"Found {len(links)} charity links on {page_link}.")
    return links


def get_charity_info(charity_url):
    """Fetches charity name and website URL."""
    html = fetch_html(charity_url)
    if not html:
        return None, None

    bs = BeautifulSoup(html, 'lxml')
    try:
        charity_name = bs.find('h1', class_='tw-text-3xl tw-font-semibold').get_text()
    except AttributeError:
        charity_name = "Name Not Found"

    try:
        charity_link_tag = bs.select_one(
            r'body > div.tw-mx-auto.tw-max-w-\[1500px\] > div.lg\:tw-mt-\[10px\].tw-mt-\[100px\].tw-flex.tw-flex-col.tw-min-h-screen.tw-mx-2 > div.tw-flex.tw-flex-col.md\:tw-flex-row > div:nth-child(1) > div > div > div.md\:tw-px-8 > div.tw-grid.tw-grid-cols-1.md\:tw-grid-cols-2 > div:nth-child(2) > div:nth-child(1) > div > div > a')
        charity_link = charity_link_tag['href'] if charity_link_tag else "URL not Found"
    except AttributeError:
        charity_link = "URL not Found"

    logging.info(f"Fetched {charity_name} - {charity_link}")
    return charity_name, charity_link


def save_to_csv(filename, data):
    """Saves the charity data to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Charity Name', 'URL'])
        writer.writerows(data)
    logging.info(f"Data saved to {filename}")


def main():
    base_url = 'https://www.charitynavigator.org/discover-charities/a-to-z-directory/'
    all_pages_links = get_all_pages_links(base_url)

    all_charity_links = []
    for page_link in all_pages_links:
        all_charity_links.extend(get_charity_links(page_link))

    charity_infos = []
    for charity_url in all_charity_links: 
        charity_name, charity_link = get_charity_info(charity_url)
        if charity_name and charity_link:
            charity_infos.append([charity_name, charity_link])

    save_to_csv('charity.csv', charity_infos)


if __name__ == "__main__":
    main()
