from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.conf import settings
import re

from tools.crawler_task import crawl

User = get_user_model()

class CountryManager(models.Manager):
    pass

class Country(models.Model):
    name = models.CharField(max_length=24, null=True, blank=True, verbose_name=_('国家名称'))
    lang_code = models.CharField(max_length=8, unique=True, verbose_name=_('语言代码'))
    url = models.CharField(max_length=128, verbose_name=_('站点链接'))

    objects = CountryManager()

    def __str__(self):
        return self.name

class QueryManager(models.Manager):
    pass

class Query(models.Model):
    keywords = models.CharField(max_length=64, verbose_name=_('查询关键字'))
    site = models.ForeignKey(Country, verbose_name=_('查询站点'))
    user = models.ForeignKey(User, verbose_name=_('查询用户'), default=1)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('查询时间'))

    objects = QueryManager()

    def __str__(self):
        return self.keywords

class QueryResultManager(models.Manager):
    pass

class QueryResult(models.Model):
    query = models.ForeignKey(Query, verbose_name=_('查询关键字'), related_name='results')
    page = models.IntegerField(default=0, null=True, blank=True, verbose_name=_('页码'))
    rank = models.IntegerField(default=0, null=True, blank=True, verbose_name=_('排名'))
    overall_rank = models.IntegerField(default=0, null=True, blank=True, verbose_name=_('整体排名'))
    title = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('商品名称'))
    price = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('商品价格'))
    orders = models.IntegerField(default=0, null=True, blank=True, verbose_name=_('订单量'))
    store = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('店铺名称'))
    credit_points = models.FloatField(default=100.0, null=True, blank=True, verbose_name=_('店铺信誉分'))
    favorate_rate = models.FloatField(default=100.0, null=True, blank=True, verbose_name=_('商品好评率'))
    rating = models.FloatField(default=100.0, null=True, blank=True, verbose_name=_('商品评分'))
    comments = models.IntegerField(default=100, null=True, blank=True, verbose_name=_('评论数'))
    img_url = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_('图片链接'))
    product_url = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_('商品链接'))
    product_code = models.CharField(max_length=32, null=True, blank=True, verbose_name=_('产品编号'))


    objects = QueryResultManager()

    def __str__(self):
        return self.title

def store_crawled_result(results, query_instance):

    for result in results:
        QueryResult.objects.create(
            query = query_instance,
            page = result['page'],
            rank = result['rank'],
            title = result['title'],
            price = result['price'],
            orders = result['orders'],
            store = result['store_name'],
            credit_points = result['favorate_rate'],
            rating = result['rating'],
            comments = result['comments'],
            img_url = result['img_url'],
            product_url = result['product_url']
        )

def query_post_save_receiver(sender, instance, *args, **kwargs):
    site = instance.site
    kw = instance.keywords
    results = crawl(site, kw, settings.PAGE_SIZE)
    store_crawled_result(results, instance)

post_save.connect(query_post_save_receiver, sender=Query)

def query_result_post_save_receiver(sender, instance, *args, **kwargs):
    # get overall_rank
    _rank = 0
    for i in range(instance.page):
        if i + 1 < instance.page:
            _rank += instance.__class__.objects.filter(page=i + 1).count()
        else:
            _rank += instance.rank

    # get product code
    product_url = instance.product_url
    _code = re.search(r'(\d+).html', product_url).group(1)

    instance.overall_rank = _rank
    instance.product_code = _code

pre_save.connect(query_result_post_save_receiver, sender=QueryResult)

