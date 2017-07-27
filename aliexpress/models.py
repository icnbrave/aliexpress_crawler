from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.conf import settings

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
    title = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('商品名称'))
    price = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('商品价格'))
    order = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('订单量'))
    store = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('店铺名称'))
    rank = models.IntegerField(default=0, null=True, blank=True, verbose_name=_('同类商品排名'))
    page_number = models.IntegerField(default=0, null=True, blank=True, verbose_name=_('所在页数'))

    objects = QueryResultManager()

    def __str__(self):
        return self.title

def store_crawled_result(result, query_instance):
    if len(result['titles']) == len(result['prices']) == len(result['orders']) == len(result['stores']):
        print("数据完整，可以保存")
    else:
        return False

    for i in range(len(result['titles'])):
        QueryResult.objects.create(query=query_instance, title=result['titles'][i], price=result['prices'][i],
                                   order=result['orders'][i], store=result['stores'][i], )

def query_post_save_receiver(sender, instance, *args, **kwargs):
    site = instance.site
    kw = instance.keywords
    result = crawl(site, kw, settings.PAGE_SIZE)
    store_crawled_result(result, instance)

post_save.connect(query_post_save_receiver, sender=Query)
