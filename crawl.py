#!python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import urllib.request
import os


idx = 1

try:
    os.mkdir('data')
except:
    pass


def download_image(image_url):
    global idx

    number_str = str(idx)
    zero_filled_number = number_str.zfill(10)

    try:
        filename, headers = urllib.request.urlretrieve(
            image_url, 'data/' + zero_filled_number + '.jpg')
        if (headers['Content-Type'] != "image/jpeg"):
            os.remove(filename)
        else:
            idx += 1
    except:
        pass


def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(
            f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    download_image(actual_image.get_attribute('src'))
                    # image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                break
        else:
            time.sleep(30)
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")
                time.sleep(2)

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


driver = webdriver.Chrome()
fetch_image_urls("f-16 in the air", 1, driver, 1)
driver.close()


# driver.get("http://www.python.org")
# assert "Python" in driver.title
# elem = driver.find_element_by_name("q")
# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
# driver.close()
