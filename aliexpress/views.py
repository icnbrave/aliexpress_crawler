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
    template_name = "home.html"
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        sites = Country.objects.all()
        context['sites'] = sites

        context['functions'] = functions
        context['last_function_id'] = int( self.request.GET.get('function', 0) )

        site_id = self.request.GET.get('site', sites.first().id)
        context['last_site_id'] = int(site_id)
        site = Country.objects.filter(id = site_id).first()

        kw = self.request.GET.get('q', None)

        user = self.request.user
        if not user.id:
            user = UserModel.objects.first()

        function_id = self.request.GET.get('function')
        # 查询关键字
        if function_id == '1':
            qs = Query.objects.filter(keywords=kw, site=Country.objects.get( id = int(site_id) ))
            query = None

            if qs.exists():
                query = qs.first()
            else:
                query = Query.objects.create(keywords=kw, site=Country.objects.get( id = int(site_id) ), user=user)

            # Query result
            context['query_requests'] = query.results.all()

        elif function_id == '2':
            # Get related keywords information
            related_keywords = get_related_keywords(site, kw)
            context['related_keywords'] = related_keywords

        elif function_id == '3':
            # Get relevant English translation of a non-English string
            en_keyword = get_english_translation(kw)
            context['en_keyword'] = en_keyword

        return context


class QueryView(CreateView):
    template_name = 'form.html'
    form_class = QueryForm

    def get_context_data(self, *args, **kwargs):
        context = super(QueryView, self).get_context_data(*args, **kwargs)
        context['title'] = '查询'
        return context
