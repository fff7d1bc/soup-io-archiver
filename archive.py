#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
import requests
import urllib.parse
from pathlib import PurePath, Path
import sys

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def einfo(msg):
    print("[INFO] >>> {}".format(msg))


def download(url, directory, session=None):
    if not session:
        session = requests.session()
    
    Path(directory).mkdir(exist_ok=True, parents=True)

    filename = PurePath(urllib.parse.unquote(urllib.parse.urlparse(url).path)).parts[-1]

    target = Path(PurePath().joinpath(directory, filename))
    target_partial = Path("{}.__partial__".format(target))

    if target.exists():
        einfo("Target {} already exists.".format(filename))
        return

    einfo("Downloading {} ...".format(url))
    with session.get(url, stream=True) as r:
        # dumb hack to ignore 404.
        if r.status_code == 404:
            return
        else:
            r.raise_for_status()

        with target_partial.open(mode='wb') as f:
            for chunk in r.iter_content(chunk_size=64*1024):
                if chunk:
                    f.write(chunk)

    target_partial.rename(target)



def scrape_post(url, soup_name, session=None):
    einfo("Scraping {} ...".format(url))

    url_parsed = urllib.parse.urlparse(url)

    if not session:
        session = requests.session()

    payload = session.get(url).content.decode('utf-8')
    bs = BeautifulSoup(payload, 'html.parser')

    images_download_directory = PurePath().joinpath('archives', soup_name, 'images')
    posts_download_directory = Path().joinpath('archives', soup_name, 'posts')

    Path(posts_download_directory).mkdir(exist_ok=True, parents=True)

    post_id = url_parsed.path.split('/')[2]

    for image in bs.find_all("meta",  property="og:image"):
        image_url = image.attrs['content']
        if image_url:
            download(image_url, images_download_directory, session=session)

    post_payload_target = Path(PurePath().joinpath(posts_download_directory, post_id))

    if not post_payload_target.exists():
        post_payload_target.write_text(payload)



def get_posts(url, session=None):
    einfo("Getting posts from {} ...".format(url))

    url_parsed = urllib.parse.urlparse(url)

    if not session:
        session = requests.session()

    payload = session.get(url).content.decode('utf-8')
    bs = BeautifulSoup(payload, 'html.parser')

    post_urls = set()

    for post_url in bs.find_all('a', href=re.compile(r'{}/post/.*'.format(url_parsed.netloc), re.IGNORECASE)):
        post_urls.add(post_url.attrs['href'])

    next_page = bs.find('a', href=re.compile(r'/since/[0-9]+\?mode=own$'), text='more posts')
    if next_page:
        next_page = urllib.parse.urljoin(url, next_page.attrs['href'])

    if not post_urls:
        print(payload)

    return post_urls, next_page


def main():
    session = requests.session()

    retry_strategy = Retry(
        total=15,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=0.5
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount('https://', adapter)
    session.mount('http://', adapter)

    domain = sys.argv[1]

    if not domain.endswith('.soup.io'):
        # custom domains will bitch about ssl cert.
        session.verify = False

    page = "https://{}".format(domain)

    while page:
        posts, page = get_posts(page, session=session)

        for post in posts:
            scrape_post(post, domain, session=session)


if __name__ == "__main__":
    main()
