from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "core/index.html"

    # def get(self, request, **kwargs):
    #     req = request.GET
    #     if request.user.is_authenticated:
    #         print('******************************************')
    #     else:
    #         print('-------------------------------')
    #
    #     return HttpResponse('NOne')