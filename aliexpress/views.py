from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, CreateView, TemplateView

from tools.crawler_task import get_related_keywords, get_english_translation

from .models import Country, Query
from .forms import QueryForm

UserModel = get_user_model()

functions = [
    {'name': '关键字查询', 'id': 1},
    {'name': '相关关键字查询', 'id': 2},
    {'name': '对应英文关键字', 'id': 3},
    {'name': '产品对应站点排名', 'id': 4},
]

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
                qs = Query.objects.filter(keywords=kw, site=Country.objects.get( id = int(site_id) ))

                if qs.exists():
                    query = qs.first()
                else:
                    query = Query.objects.create(keywords=kw, site=Country.objects.get( id = int(site_id) ), pages=pages, user=user)
                qlist.append(query)

            # Query result
            query_results = []
            for q in qlist:
                query_results += q.results.all()

            context['query_results'] = query_results

        context['title'] = '关键字查询'

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

        context['title'] = '相关关键字查询'

        # Get related keywords information
        if kw:
            related_keywords = get_related_keywords(site, kw)
            context['related_keywords'] = related_keywords

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

            # search for each kwywords, and map searched keyword to the required keywords
            result = [(kw, get_english_translation(kw)) for kw in kws_arr]

            context['result'] = result

        context['title'] = '英文翻译查询'

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

        context['title'] = '产品在不同站点排名'
        context['results'] = results

        return context
