#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/19 10:43
# @Author  : WuFan

import bs4
import requests
import re
import xlwt
import datetime

date = datetime.datetime.now().strftime('%Y-%m-%d')  # 给文件打上时间戳，便于数据更新
url = 'https://www.aliexpress.com/wholesale'  # 网址
payload = {'SearchText': 'nike', 'page': '1', 'ie': 'utf8', 'g': 'y'}  # 字典传递url参数

# 初始化数据容器
title = []
price = []
order = []
store = []


def get_page_html(site, kw, page):
    payload['SearchText'] = kw
    payload['page'] = page
    url = '{site}/wholesale'.format(site=site)
    resp = requests.get(url, params=payload)
    return resp

def crawl(site, kw, pages):
    """
    Crawling according to the keywords {kw} on {site} in the first {pages} pages
    :return: {'title':[], 'price':[], 'order':[], 'store':[]}
    """
    for i in range(0, pages):  # 循环5次，就是5个页的商品数据
        page = i + 1  # 此处为页码，根据网页参数具体设置
        resp = get_page_html(site.url, kw, page)
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        print(resp.url)  # 打印访问的网址
        resp.encoding = 'utf-8'  # 设置编码

        # 标题
        all_title = soup.find_all('a', class_=re.compile("history-item product"))
        for j in all_title:
            soup_title = bs4.BeautifulSoup(str(j), "html.parser", )
            title.append(soup_title.a['title'])
        # 价格
        all_price = soup.find_all('span', itemprop="price")
        for k in all_price:
            soup_price = bs4.BeautifulSoup(str(k), "html.parser")
            price.append(soup_price.span.string)
        # 订单量
        all_order = soup.find_all('a', class_=re.compile("order-num-a"))
        for l in all_order:
            soup_order = bs4.BeautifulSoup(str(l), "html.parser")
            order.append(soup_order.em.string)
        # 店铺名称
        all_store = soup.find_all('div', class_="store-name util-clearfix")
        for m in all_store:
            soup_store = bs4.BeautifulSoup(str(m), "html.parser")
            store.append(soup_store.a.string)

    result = {'titles': title, 'prices': price, 'orders': order, 'stores': store}
    return result


#
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