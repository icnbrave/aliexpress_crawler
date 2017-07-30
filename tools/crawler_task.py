#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/19 10:43
# @Author  : WuFan

import bs4
import requests
import re
import xlwt
import datetime
import json
import traceback

date = datetime.datetime.now().strftime('%Y-%m-%d')  # 给文件打上时间戳，便于数据更新
url = 'https://www.aliexpress.com/wholesale'  # 网址
payload = {'SearchText': 'nike', 'page': '1', 'ie': 'utf8', 'g': 'y'}  # 字典传递url参数

def get_page_html(site, kw, page):
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'Mozilla/5.0'
        }
    )
    payload['SearchText'] = kw
    payload['page'] = page
    url = '{site}/wholesale'.format(site=site)
    resp = requests.get(url, params=payload)
    return resp

def crawl(site, kw, pages):
    """
    Crawling according to the keywords {kw} on {site} in the first {pages} pages
    """
    results = []
    for i in range(0, pages):  # 循环5次，就是5个页的商品数据
        page = i + 1  # 此处为页码，根据网页参数具体设置
        resp = get_page_html(site.url, kw, page)
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        print(resp.url)  # 打印访问的网址
        resp.encoding = 'utf-8'  # 设置编码

        items = soup.find_all('div', class_='item')
        for index, item in enumerate(items):
            d = {'normal':True} # 初始化采集数据，过滤那些只有图片，没有产品描述的商品

            # 页数
            d['page'] = page

            # 当前页排名
            d['rank'] = index+1

            if not item.find('div', class_='info'):
                d['normal'] = False
                continue

            try:
                # 产品链接
                d['product_url'] = 'https:' + item.a['href']

                # 图片链接
                try:
                    d['img_url']  = 'https:' + item.img['src']
                except:
                    d['img_url'] = 'https:' + item.img['image-src']

                # 产品标题
                d['title'] = item.find('a', class_=re.compile('history-item product'))['title']

                # 产品价格
                d['price'] = item.find('span', itemprop="price").text

                # 有些有评价信息，有些没有
                try:
                    # 产品好评率
                    d['favorate_rate'] = re.search(r'(\d+.\d)%;', item.find('span', class_='rate-percent')['style']).group(1)

                    # 评分
                    d['rating'] = re.search(r'(\d+.\d+)', item.find('span', class_='star star-s')['title']).group(1)

                    # 评论数
                    d['comments'] = re.search(r'(\d+)', item.find('a', class_=re.compile('rate-num')).text).group(1)
                except:
                    d['favorate_rate'] = '100.0'
                    d['rating'] = 5.0
                    d['comments'] = 0


                # 订单量
                d['orders'] = re.search(r'(\d+)', item.find('em').text).group(1)

                # 店铺名
                d['store_name'] = item.find('div', class_='store-name util-clearfix').a.text

                # 店铺链接
                d['store_url'] = 'https:' + item.find('div', class_='store-name util-clearfix').a['href']

                results.append(d)
            except:
                traceback.print_exc()
                print(d['product_url'])
                print(item.find('span', class_='rate-percent'))


    return results


def get_related_keywords(site, kw):
    s = requests.Session()
    s.get(site.url)

    url = "https://connectkeyword.aliexpress.com/lenoIframeJson.htm?varname=intelSearchData&__number=2&catId=0&keyword={kw}".format(kw=kw)
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




#
# # 数据验证
# print(len(title))
# print(len(price))
# print(len(order))
# print(len(store))
#
# if len(title) == len(price) == len(order) == len(store):
#     print("数据完整，生成 %d 组商品数据！" % len(title))
#
# # 写入excel文档
# print("正在写入excel表格...")
# wookbook = xlwt.Workbook(encoding='utf-8')  # 创建工作簿
# data_sheet = wookbook.add_sheet('demo')  # 创建sheet
#
# # 生成每一行数据
# for n in range(len(title)):
#     data_sheet.write(n, 0, n + 1)
#     data_sheet.write(n, 1, title[n])  # n 表示行， 1 表示列
#     data_sheet.write(n, 2, price[n])
#     data_sheet.write(n, 3, order[n])
#     data_sheet.write(n, 4, store[n])
#
# wookbook.save("%s-%s.xls" % (payload['SearchText'], date))
# print("写入excel表格成功！")

def get_english_translation(kw):
    s = requests.Session()

    url = "https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20170729014525&SearchText={kw}".format(kw=kw)
    resp = s.get(url)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    script = soup.find_all('script')[1]
    result = re.search(r'"enKeyword":"([\w| ]+)"', script.string)
    return result.group(1)