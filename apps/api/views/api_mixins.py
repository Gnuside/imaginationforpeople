
from tastypie.exceptions import BadRequest, ApiFieldError
from django.core.exceptions  import ValidationError

from tastypie.resources import csrf_exempt

# FIXME: remove
import pprint
pp = pprint.PrettyPrinter(indent=4)



###
### BIG FAT WARNING : THIS FILE SHOULD NOT BE USED AS IS IN PRODUCTION

### WHAT WORKS AND SHOULD BE USED
### - def determine_format() + the try part of def wrap_view():

### WHAT IS BROKEN AND SHOULD BE FIXED FIRST
### - the exception handling of wrap_view() + error_response()

### STILL UNRESOLVED AND NEEDS WORK
### - writing correct urls in meta.next and meta.previous


class ResourceFixerMixin(object):
    """
    A Mixin with multiple fixes to adapt default tastypie resource.
    
    1. Force to the format from the request.format attribute. 
    If format is not specified, return an error instead of 
    negociating format automatically, to make sure an URL always
    returns the same type of content.
    """
    
    def determine_format(self, request, **kwargs):
        """
        Detect format parameter instead of negotiating it
        """
        #print("ResourceFixerMixin.determine_format")
        #pp.pprint(request)
        if (hasattr(request, 'format') and request.format in self._meta.serializer.formats):
            return self._meta.serializer.get_mime_for_format(request.format)    
        raise BadRequest("Missing format extension")


    def wrap_view(self, view):
        """
        Use detected format parameter in view (instead of the negotiated one)
        
        Wraps views to return custom error codes instead of generic 500's
        """
        @csrf_exempt
        
        def wrapper(request, *args, **kwargs):
            try:
                # set request format for determine_format which is called later
                request.format = kwargs.pop('format', None)
                
                wrapped_view = super(ResourceFixerMixin, self).wrap_view(view)
                response = wrapped_view(request, *args, **kwargs)

                if request.is_ajax():
                    patch_cache_control(response, no_cache=True)

                print "ResourceFixerMixin.wrap_view.wrapper - no exeptions :-("
                # response is a HttpResponse object, so follow Django's instructions
                # to change it to your needs before you return it.
                # https://docs.djangoproject.com/en/dev/ref/request-response/
                return response

            except (BadRequest, ApiFieldError), e:
                print "ResourceFixerMixin.wrap_view.wrapper - BadRequest / ApiFieldError"
                return HttpBadRequest({'code': 666, 'message':e.args[0]})

            except ValidationError, e:
                # Or do some JSON wrapping around the standard 500
                print "ResourceFixerMixin.wrap_view.wrapper - ValidationError"
                return HttpBadRequest({'code': 777, 'message':', '.join(e.messages)})

            except Exception, e:
                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                print "ResourceFixerMixin.wrap_view.wrapper - unknown Exception !"
                pp.pprint(request)
                pp.pprint(e)
                return self._handle_500(request, e)
                
        return wrapper

    def error_response(self, request, errors, response_class=None):
        """
        Define a custom error response with a meta object & such
        """
        print "ResourceFixerMixin.error_response -|"
        pp.pprint(request)
        pp.pprint(errors)
        fixed_errors = {
           "meta" : {
              "pif" : "paf"
           },
           "objects" : errors
        }
        return super(ResourceFixerMixin, self).error_response(request, errors, response_class)

