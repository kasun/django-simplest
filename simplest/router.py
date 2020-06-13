import os
import json
from collections import defaultdict

from django.urls import include, path, resolve
from django.http import HttpResponse, JsonResponse

from .path import Path


class Router:

    def __init__(self, parent_router=None, path=None):
        self.parent_router = parent_router
        self.path = path
        self.children = []
        self.route_map = defaultdict(dict)

        if self.parent_router:
            self.parent_router.register_child(self)

    def __repr__(self):
        return f'{self.__class__}: {self.path}'

    def view(self, path, methods, csrf_exempt=False, **kwargs):
        """ router view """
        def wrapper(fn):
            if csrf_exempt:
                fn.csrf_exempt = True
            def inner(*args, **kwargs):
                return fn(*args, **kwargs)

            if self.path:
                full_path = os.path.join(self.get_full_path(), path.lstrip('/'))
            else:
                full_path = path

            for method in methods:
                path_instance = Path(full_path, method, fn, auth_required=kwargs.get('auth', False))
                self.route_map[full_path][method] = path_instance

            return inner

        return wrapper

    def get(self, path, csrf_exempt=False, **kwargs):
        """ view for GET method """
        def wrapper(fn):
            if csrf_exempt:
                fn.csrf_exempt = True
            def inner(*args, **kwargs):
                return fn(*args, **kwargs)

            if self.path:
                full_path = os.path.join(self.get_full_path(), path.lstrip('/'))
            else:
                full_path = path

            path_instance = Path(full_path, 'GET', fn, auth_required=kwargs.get('auth', False))
            self.route_map[full_path]['GET'] = path_instance
            return inner

        return wrapper

    def post(self, path, csrf_exempt=False, **kwargs):
        """ view for POST method """
        def wrapper(fn):
            if csrf_exempt:
                fn.csrf_exempt = True
            def inner(*args, **kwargs):
                return fn(*args, **kwargs)

            if self.path:
                full_path = os.path.join(self.get_full_path(), path.lstrip('/'))
            else:
                full_path = path

            path_instance = Path(full_path, 'POST', fn, auth_required=kwargs.get('auth', False))
            self.route_map[full_path]['POST'] = path_instance
            return inner

        return wrapper

    def generate_url_patterns(self):
        patterns = []
        for path_str in self.route_map.keys():
            patterns.append(path(path_str, self.route))

        for child in self.children:
            patterns.extend(child.generate_url_patterns())

        return patterns

    def get_full_path(self):
        """ Generate full path of this router using parent router paths """
        if self.parent_router:
            full_path = os.path.join(self.parent_router.get_full_path().lstrip('/'), self.path.lstrip('/'))
        else:
            full_path = self.path

        return full_path

    def register_child(self, child):
        """ Register a child router
            Args:
                child (Router) """
        self.children.append(child)

    def route(self, request, **kwargs):
        route_path = resolve(request.path).route
        try:
            path_object = self.route_map[route_path][request.method]
        except KeyError:
            return JsonResponse({'error': True, 'reason': f'Method not allowed: {request.method}'}, status=400)

        if path_object.auth_required and not request.user.is_authenticated:
            return JsonResponse({'error': True, 'reason': f'Authentication Required'}, status=401)

        if request.method == 'POST':
            try:
                request.json = json.loads(request.body)
            except Exception:
                pass

        res = path_object.view(request, **kwargs)
        if isinstance(res, HttpResponse):
            return res

        return JsonResponse(res, safe=False)
    

def router(parent_router=None, path=None):
    return Router(parent_router, path)
