# -*- encoding: utf-8 -*-
#
# This file is part of I4P.
#
# I4P is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# I4P is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
# 
# You should have received a copy of the GNU Affero Public License
# along with I4P.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.models import User
from django.utils import translation
from django.core.urlresolvers import NoReverseMatch, reverse, resolve, Resolver404, get_script_prefix

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash
from tastypie.throttle import CacheDBThrottle
from tastypie.paginator import Paginator


from apps.i4p_base.models import Location
from apps.project_sheet.models import Answer, Objective, I4pProject, I4pProjectTranslation, Topic,\
    ProjectPicture, ProjectReference, ProjectVideo
from apps.project_sheet.utils import get_project_translations_from_parents


from .api_mixins import ResourceFixerMixin
#from .api_helper import FormatUrlHelper

# FIXME: remove
import pprint
pp = pprint.PrettyPrinter(indent=4)


### UTILITY CLASSES

class I4pProjectResource(ResourceFixerMixin,ModelResource):
    class Meta:
        queryset = I4pProject.objects.all()
        include_resource_uri = False
        #fields = ['country']

### ENTRY POINT CLASSES

class I4pProjectxTranslationListResource(ResourceFixerMixin,ModelResource):
    project = fields.ForeignKey(I4pProjectResource, 
         use_in='detail', 
         attribute='master', 
         full=True
    )
    
    class Meta:
        queryset = I4pProjectTranslation.objects.all()
        include_resource_uri = False
        #fields = ['country']
        resource_name = 'projectx/list'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        fields = ['id', 'slug','language_code','title','baseline', 'project']
        filtering = {
            "language_code": 'exact'
        }

    def detail_uri_kwargs(self, bundle_or_obj):
        return
   
    def prepend_urls(self):
        array = [
            url(r"^(?P<resource_name>%s/all)\.(?P<format>\w+)$" % self._meta.resource_name, 
               self.wrap_view('dispatch_all'), 
               name="api_dispatch_all"),
            url(r"^(?P<resource_name>%s/bestof)\.(?P<format>\w+)$" % self._meta.resource_name,
               self.wrap_view('dispatch_bestof'), 
               name="api_dispatch_bestof"),
            url(r"^(?P<resource_name>%s/latest)\.(?P<format>\w+)$" % self._meta.resource_name, 
               self.wrap_view('dispatch_latest'), 
               name="api_dispatch_latest"),
        ]
        return array

    def dispatch_all(self, request, **kwargs):
        print("ProjectxListResource.dispatch_all")
        pp.pprint(kwargs)
        return self.dispatch('list', request, **kwargs)

    def dispatch_bestof(self, request, **kwargs):
        print("ResourceFixerMixin.dispatch_bestof")
        # = 'projectx/list/bestof'
        self._meta.queryset = I4pProjectTranslation.objects.filter(master__best_of=True) #.order_by('?')
        pp.pprint(kwargs)
        #print(reverse('api_dispatch_bestof', kwargs={'resource_name': 'projectx/list', 'api_name': 'v1'}))
        kwargs['format'] = request.format
        return self.dispatch('list', request, **kwargs)


class I4pProjectxTranslationResource(ResourceFixerMixin,ModelResource):
    class Meta:
        queryset = I4pProjectTranslation.objects.all()
        include_resource_uri = True
        #fields = ['country']
        resource_name = 'projectx'
        fields = ['id', 'slug','language_code','title','baseline']
        
    def prepend_urls(self):
        array = [
            url(r"^(?P<resource_name>%s)/random\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
        ]
        return array


