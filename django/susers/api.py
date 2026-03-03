from django.http import HttpResponse
import simpleserver.settings as settings
from susers.models import User
import jwt
import json
import pdb


from django.http import HttpResponse
import simpleserver.settings as settings
from susers.models import User
import jwt
import json
import pdb


def token_required():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
#            pdb.set_trace()
            try:
                auth = request.COOKIES.get('token','')
                request.redata = {}
                request.redata['token'] = False
            except:
                auth = ''
                request.redata = {}
                request.redata['token'] = False
            if auth:
                try:
                    dict = jwt.decode(auth, settings.SECRET_KEY, algorithms=['HS256'])
                    user_id = dict.get('user_id')
                    request.redata['token'] = True
#                except jwt.ExpiredSignatureError:
#                    return HttpResponse(json.dumps({"code": 0, "message": "Token expired"}))
#                except jwt.InvalidTokenError:
#                    return HttpResponse(json.dumps({"code": 0, "message": "Invalid token"}))
                except Exception as e:
                    request.user = ''
                    return view_func(request, *args, **kwargs)


#                    return HttpResponse(json.dumps({"code": 0, "message": "Can not get user object"}))
                try:
                    request.user = User.objects.get(id=user_id)
                except:
                    pass
#                    return HttpResponse(json.dumps({"code": 0, "message": "User Does not exist"}))

                return view_func(request, *args, **kwargs)
            else:
                request.user = ''
                return view_func(request, *args, **kwargs)
#                return HttpResponse(json.dumps({"code": 0, "message": "Error authenticate header"}))

        return _wrapped_view

    return decorator
