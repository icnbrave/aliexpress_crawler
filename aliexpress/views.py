from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import View, CreateView, TemplateView
from .models import Country, Query
from .forms import QueryForm

UserModel = get_user_model()

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        sites = Country.objects.all()
        context['sites'] = sites

        site_id = self.request.GET.get('site', sites.first().id)
        kw = self.request.GET.get('q', None)
        errors = []
        if not kw:
            errors.append('请输入查询关键字')
            context['errors'] = errors
            return context

        user = self.request.user
        if not user.id:
            user = UserModel.objects.first()

        qs = Query.objects.filter(keywords=kw, site=Country.objects.get( id = int(site_id) ))
        query = None

        if qs.exists():
            query = qs.first()
        else:
            query = Query.objects.create(keywords=kw, site=Country.objects.get( id = int(site_id) ), user=user)

        # Query result
        context['results'] = query.results.all()
        context['last_site_id'] = int(site_id)

        return context


class QueryView(CreateView):
    template_name = 'form.html'
    form_class = QueryForm

    def get_context_data(self, *args, **kwargs):
        context = super(QueryView, self).get_context_data(*args, **kwargs)
        context['title'] = '查询'
        return context
