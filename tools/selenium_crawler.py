# encoding = utf-8

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time, datetime
import os
import re
from urllib.parse import urlencode
from tools.crawler_task import auth
import traceback

from tools import config

date = datetime.datetime.now().strftime('%Y-%m-%d')  # 给文件打上时间戳，便于数据更新
SEARCH_URL = 'https://www.aliexpress.com/wholesale'  # 网址

class AliCrawler:

    def __init__(self):
        self._driver = None

    def get_driver(self):
        if not self._driver:
            chromedriver = config.CHROMEDRIVER_PATH
            cap = DesiredCapabilities.CHROME
            cap['pageLoadStrategy'] = 'none'

            os.environ['webdriver.chrome.driver'] = chromedriver
            driver = webdriver.Chrome(chromedriver, desired_capabilities=cap)

            driver.maximize_window()
            self._driver = driver
            return self._driver

        return self._driver

    def login(self):
        driver = self.get_driver()
        wait = WebDriverWait(driver, 30)

        driver.get(config.LOGIN_URL)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#alibaba-login-box')))

        login_frame = driver.find_element_by_id('alibaba-login-box')
        driver.switch_to.frame(login_frame)

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#fm-login-id')))
        driver.find_element_by_css_selector('#fm-login-id').send_keys(config.LOGIN_USER)
        driver.find_element_by_css_selector('#fm-login-password').send_keys(config.LOGIN_PASSWD)
        driver.find_element_by_css_selector('#fm-login-submit').click()

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#form-searchbar')))
        driver.execute_script('window.stop();')

    def search(self, site_url, kw, page):
        payload = {}
        payload['SearchText'] = kw
        payload['page'] = page
        payload['g'] = 'y'
        url = '{site}/wholesale?{params_string}'.format(site=site_url, params_string=urlencode(payload))

        driver = self.get_driver()

        wait = WebDriverWait(driver, 20)

        driver.get(url)

        time.sleep(2)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#hs-below-list-items')))
        driver.execute_script('window.stop();')

        self.close_layer()

    def parse(self, site, kw, pages):
        """
        Crawling according to the keywords {kw} on {site} in the first {pages} pages
        """
        total_searched = None
        results = []
        item_num = 0

        driver = self.get_driver()

        for i in range(0, pages):  # 循环5次，就是5个页的商品数据
            init_rank = 0

            if total_searched and item_num + 40 >= total_searched:
                break

            page = i + 1  # 此处为页码，根据网页参数具体设置
            self.search(site.url, kw, page)
            print(driver.current_url)

            # Get total searched count
            if page == 1:
                r = driver.find_element_by_css_selector('strong.search-count').text
                total_searched = int(r.replace(',', ''))

            items = driver.find_elements_by_css_selector('div.item')
            for index, item in enumerate(items):
                item_num += 1

                d = {'normal':True} # 初始化采集数据，过滤那些只有图片，没有产品描述的商品

                # 页数
                d['page'] = page

                try:
                    item.find_element_by_css_selector('div.info')
                except:
                    # traceback.print_exc()
                    d['normal'] = False
                    continue

                # 当前页排名
                init_rank += 1
                d['rank'] = init_rank

                try:
                    # 产品链接
                    d['product_url'] = item.find_element_by_css_selector('a').get_attribute('href')

                    # 图片链接
                    img_url = item.find_element_by_css_selector('img.picCore').get_attribute('src')
                    if not img_url:
                        img_url = 'https:' + item.find_element_by_css_selector('img.picCore').get_attribute('image-src')
                    d['img_url'] = img_url


                    # 产品标题
                    d['title'] = item.find_element_by_css_selector('a.history-item.product').get_attribute('title')

                    # 产品价格
                    d['price'] = item.find_element_by_css_selector('span[itemprop="price"]').text

                    # 有些有评价信息，有些没有
                    try:
                        # 产品好评率
                        rate_string = item.find_element_by_css_selector('span.rate-percent').get_attribute('style')
                        d['favorate_rate'] = re.search(r'(\d+.\d)%;', rate_string).group(1)

                        # 评分
                        rating = item.find_element_by_css_selector('span.star.star-s').get_attribute('title')
                        d['rating'] = re.search(r'(\d+.\d+)', rating).group(1)

                        # 评论数
                        comment_count = item.find_element_by_css_selector('a.rate-num').text
                        d['comments'] = re.search(r'(\d+)', comment_count).group(1)
                    except:
                        d['favorate_rate'] = '100.0'
                        d['rating'] = 5.0
                        d['comments'] = 0


                    # 订单量
                    order = item.find_element_by_css_selector('em').text
                    d['orders'] = re.search(r'(\d+)', order).group(1)

                    # 店铺名
                    store = item.find_element_by_css_selector('div.store-name.util-clearfix a')
                    d['store_name'] = store.get_attribute('title')

                    # 店铺链接
                    d['store_url'] = store.get_attribute('href')

                    results.append(d)
                except:
                    traceback.print_exc()
                    print(d['product_url'])
                    print(item.find('span', class_='rate-percent'))

        return results


    def get_related_keywords(self, site, kw):
        url = "https://connectkeyword.aliexpress.com/lenoIframeJson.htm?varname=intelSearchData&__number=2&catId=0&keyword={kw}".format(kw=kw)

        s = auth()

        res = s.get(url)

        if not res:
            return None
        try:
            tmp = res.text.split('=')[-1].strip()
            true = True
            false = False

            return eval(tmp)['keyWordDTOs']
        except:
            return None

    def get_english_translation(self, kw):
        site_url = 'https://www.aliexpress.com'
        self.search(site_url, kw, 1)

        driver = self.get_driver()
        script = driver.find_elements_by_css_selector('head script[type="text/javascript"]')[0]
        # for index, script in enumerate(scripts):
        #     print(index, script.get_attribute('innerHTML'))
        tmp = script.get_attribute('innerHTML')
        result = re.search(r'"enKeyword":"([\w| ]+)"', tmp)
        return result.group(1)

    def close_layer(self):
        driver = self.get_driver()
        try:
            elements = driver.find_elements_by_css_selector('.close-layer')
            if elements.__len__() > 0:
                elements[0].click()
        except:
            pass