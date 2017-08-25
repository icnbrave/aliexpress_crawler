from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, CreateView, TemplateView

from tools.crawler_task import get_page_resp

from .models import Country, Query,RelatedQuery,RelatedQueryResult
from .forms import QueryForm

from tools.selenium_crawler import AliCrawler

from tools import config

UserModel = get_user_model()

class HomeView( LoginRequiredMixin, TemplateView):
    template_name = "kw_search.html"
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        sites = Country.objects.all()
        context['sites'] = sites

        site_ids = self.request.GET.getlist('site', [sites.first().id])

        kw = self.request.GET.get('q', None)

        pages = self.request.GET.get('pages', '1')
        pages = int(pages)

        user = self.request.user
        if not user.id:
            user = UserModel.objects.first()

        # 查询关键字
        if kw:
            qlist = []

            for site_id in site_ids:
                if config.SKIP_CRAWL_IF_EXIST:
                    qs = Query.objects.filter(keywords=kw, site=Country.objects.get( id = int(site_id) ))

                    if qs.exists():
                        query = qs.first()
                    else:
                        query = Query.objects.create(keywords=kw, site=Country.objects.get( id = int(site_id) ), pages=pages, user=user)
                else:
                    query = Query.objects.create(keywords=kw, site=Country.objects.get(id=int(site_id)), pages=pages,
                                                 user=user)

                qlist.append(query)

            # Query result
            query_results = []
            for q in qlist:
                query_results += q.results.all()

            context['query_results'] = query_results

        context['title'] = '潜力款分析'

        return context



class RelatedKWSearchView( LoginRequiredMixin, TemplateView):
    template_name = "related_kw_search.html"
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super(RelatedKWSearchView, self).get_context_data(**kwargs)

        sites = Country.objects.all()
        context['sites'] = sites

        site_id = self.request.GET.get('site', sites.first().id)
        context['last_site_id'] = int(site_id)
        site = Country.objects.filter(id = site_id).first()

        kw = self.request.GET.get('q', None)

        context['title'] = '下拉词分析'

        # Get related keywords information
        if kw:
            query = RelatedQuery.objects.create(keywords=kw, site=Country.objects.get(id=int(site_id)), user=self.request.user)

            crawler = AliCrawler()
            crawler.login()

            related_keywords = crawler.get_related_keywords(site, kw)
            context['related_keywords'] = related_keywords

            crawler.get_driver().quit()

            context['related_keywords'] = related_keywords
            context['export_url'] = '/admin/aliexpress/relatedqueryresult/?query__id__exact={q_id}'.format(q_id=query.id)

            if related_keywords:
                for kw in related_keywords:
                    RelatedQueryResult.objects.create(query=query, keywords = kw['keywords'], count = kw['count'])


        return context



class EnKWSerachView( LoginRequiredMixin, TemplateView):
    template_name = "enkw_search.html"
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super(EnKWSerachView, self).get_context_data(**kwargs)

        sites = Country.objects.all()
        context['sites'] = sites

        site_id = self.request.GET.get('site', sites.first().id)
        context['last_site_id'] = int(site_id)
        site = Country.objects.filter(id = site_id).first()

        kws = self.request.GET.get('q', None)

        pages = self.request.GET.get('pages', '1')
        pages = int(pages)

        user = self.request.user
        if not user.id:
            user = UserModel.objects.first()

        # Get relevant English translation of a non-English string

        if kws:
            # split keywords, and remove space in begin and end of the string
            kws_arr = kws.split(',')
            kws_arr = [kw.strip() for kw in kws_arr]

            crawler = AliCrawler()
            crawler.login()

            # search for each kwywords, and map searched keyword to the required keywords
            result = [(kw, crawler.get_english_translation(kw)) for kw in kws_arr]

            crawler.get_driver().quit()

            context['result'] = result

        context['title'] = '小语种翻译'

        return context


class RankSerachView( LoginRequiredMixin, TemplateView):
    template_name = "rank_by_id_search.html"
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super(RankSerachView, self).get_context_data(**kwargs)

        sites = Country.objects.all()
        context['sites'] = sites

        product_id = self.request.GET.get('product_id', None)
        kw = self.request.GET.get('q', None)

        # get selected site id(s)
        sites_selected = self.request.GET.getlist('sites', None)
        results = []
        if product_id and sites_selected and kw:
            # Get the query for each site
            for site_selected in sites_selected:
                site = Country.objects.filter(id=site_selected).first()
                qs1 = Query.objects.filter(site=site, keywords=kw)
                if qs1.exists():
                    query_instance = qs1.first()
                else:
                    d = (site.name, '{0} 在该站点尚未爬取数据'.format(kw))
                    results.append(d)
                    continue

                qs = query_instance.results.filter(product_code=product_id)
                if qs.exists():
                    d = (site.name, qs.first().overall_rank)
                else:
                    d = (site.name, '{0} 在该站点抓取的数据中，没有找到该产品'.format(kw))
                results.append(d)

        context['title'] = '国家站点排名'
        context['results'] = results

        return context

class PreView(LoginRequiredMixin, TemplateView):
    template_name = 'preview.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super(PreView, self).get_context_data(**kwargs)

        sites = Country.objects.all()
        context['sites'] = sites

        site_id = self.request.GET.get('site', sites.first().id)
        site = Country.objects.filter(id=site_id).first()

        kw = self.request.GET.get('q', None)

        user = self.request.user
        if not user.id:
            user = UserModel.objects.first()

        # 查询关键字
        if kw:
            payload = {
                "loginId": "121697524@qq.com",
                "password": "q1w2e3r4",
            }

            LOGIN_URL = 'https://login.aliexpress.com/buyer.htm?spm=2114.12010608.1000002.4.EihgQ5&return=https%3A%2F%2Fwww.aliexpress.com%2Fstore%2F1816376%3Fspm%3D2114.10010108.0.0.fs2frD&random=CAB39130D12E432D4F5D75ED04DC0A84'

            import requests
            session_requests = requests.session()
            session_requests.get(LOGIN_URL)
            session_requests.post(LOGIN_URL, data=payload)
            resp = get_page_resp(session_requests, site.url, kw, 1)
            context['first_page_html'] = resp.text

        context['title'] = '查找第一页预览'

        return context