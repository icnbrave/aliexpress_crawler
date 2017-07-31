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

        site_id = self.request.GET.get('site', sites.first().id)
        context['last_site_id'] = int(site_id)
        site = Country.objects.filter(id = site_id).first()

        kw = self.request.GET.get('q', None)

        pages = self.request.GET.get('pages', '1')
        pages = int(pages)

        user = self.request.user
        if not user.id:
            user = UserModel.objects.first()

        # 查询关键字
        if kw:
            qs = Query.objects.filter(keywords=kw, site=Country.objects.get( id = int(site_id) ))
            query = None

            if qs.exists():
                query = qs.first()
            else:
                query = Query.objects.create(keywords=kw, site=Country.objects.get( id = int(site_id) ), pages=pages, user=user)

            # Query result
            context['query_requests'] = query.results.all()


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

