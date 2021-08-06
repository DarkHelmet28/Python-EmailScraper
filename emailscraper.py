from bs4 import BeautifulSoup as bs
import requests
import requests.exceptions as rqex
import urllib.parse as urlparse
from collections import deque
import re
import argparse as arg

urls = None
scraped_urls = None
emails = None

def get_arguments():
    """Get arguments from the command line"""
    parser = arg.ArgumentParser()
    parser.add_argument('-t', '--target', dest='target', help='The target URL')
    parser.add_argument('-l', '--limit', dest='limit', help='The Maximum number of URL to scan', default=100)
    options = parser.parse_args()
    if not options.target:
        options = None
    return options

def mail_scraper(target_url:str, limit:int):
    """Find emails in a target URL"""
    global urls, scraped_urls, emails
    urls = deque([target_url])
    scraped_urls = set()
    emails = set()

    count = 0
    try:
        while len(urls):
            count += 1
            if count == limit:
                break

            url = urls.popleft()
            scraped_urls.add(url)
            parts = urlparse.urlsplit(url)
            base_url = '{0.scheme}://{0.netloc}'.format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url

            print(f'[{count}] Processing {url}')
            try:
                response = requests.get(url)
            except (rqex.MissingSchema, rqex.ConnectionError, rqex.InvalidURL):
                continue
            check_mail(response)
            find_urls(response, base_url, path)
    except KeyboardInterrupt:
        print('[-] Closing!!')
    print_mail()

def find_urls(response, base_url, path):
    """Find new URL in the response"""
    global urls, scraped_urls
    soup = bs(response.text, features='lxml')
    for anchor in soup.find_all("a"):
        link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
        if link.startswith('/'):
            link = base_url + link
        elif not link.startswith('http'):
            link = path + link
        if not link in urls and not link in scraped_urls:
            urls.append(link)

def check_mail(response):
    """Check if the response contains valid mails"""
    global emails
    new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
    emails.update(new_emails)

def print_mail():
    print(f'\n[+] Found {len(emails)} mails:')
    for mail in emails:
        print(mail)


if __name__ == '__main__':
    optionsValues = get_arguments()
    if optionsValues:
        target_URL = str(optionsValues.target)
        max_limit = int(optionsValues.limit)
        mail_scraper(target_URL, max_limit)
    else:
        target_URL = input('[>] Enter Target URL To Scan: ')
        max_limit = int(input('[>] Enter the Number of maximum scan: '))
        print('\n')
        mail_scraper(target_URL, max_limit)
        

            