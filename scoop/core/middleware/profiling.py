# coding: utf-8
import cProfile
import logging
import os
import re
import sys
from functools import reduce
from operator import add
from time import time

import psutil
from django.conf import settings
from django.db import connection
from django.template.context import RequestContext
from django.template.loader import render_to_string

from scoop.core.util.django.middleware import MiddlewareBase
from scoop.core.util.django.templateutil import render_to_code

logger = logging.getLogger(__name__)


class ProfilerMiddleware(MiddlewareBase):
    """ Middleware de profilage """

    # Constantes
    HTML_SIGNAL = "<!-- debug -->"
    profiler = None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """ Traiter la vue """
        if settings.DEBUG and request.user.is_staff:
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def __call__(self, request):
        """ Traiter la réponse """
        response = self.get_response(request)
        if settings.DEBUG and request.user.is_staff and self.profiler is not None:
            self.profiler.create_stats()
            stats = self.profiler.getstats()
            stats = sorted(stats, key=lambda k: -k.inlinetime)
            total_time = reduce(lambda x, y: x + y.inlinetime, stats, 0)
            total_calls = reduce(lambda x, y: x + y.callcount, stats, 0)
            insert_pos = str(response.content, 'utf-8').rfind(ProfilerMiddleware.HTML_SIGNAL)
            if insert_pos != -1:
                output = render_to_string('core/middleware/profiling.html', {'stats': stats, 'total_time': total_time, 'total_calls': total_calls},
                                          context_instance=RequestContext(request))
                response.content = response.content.decode('utf-8').replace(ProfilerMiddleware.HTML_SIGNAL, output, 1)
            elif 'profile' in request.GET:
                output = render_to_string('core/middleware/profiling.html', {'stats': stats, 'total_time': total_time, 'total_calls': total_calls},
                                          context_instance=RequestContext(request))
                response.content += output
        return response


class PageStatsMiddleware(object):
    """ Middleware de statistiques de performance de la page """

    # Constantes
    REGEXP = r'(?P<cmt><!--\s*STATS:(?P<fmt>.*?)\s*-->)'

    def process_request(self, request):
        """ Traiter la requête """
        connection.use_debug_cursor = True  # Activer le DEBUG de la connexion
        self.start = time()
        return None

    def process_response(self, request, response):
        """ Traiter la réponse """
        self.queries = len(connection.queries)
        self.elapsed = time() - self.start
        self.db_time = reduce(add, [float(q['time']) for q in connection.queries]) if connection.queries else 0.0
        self.py_time = self.elapsed - self.db_time
        # Remplacer <!-- [format] --> par les résultats d'analyse
        stats = {'elapsed': self.elapsed, 'py_time': self.py_time, 'db_time': self.db_time, 'queries': self.queries}
        if response.content:
            output = response.content
            regexp = re.compile(PageStatsMiddleware.REGEXP)
            match = regexp.search(output)
            if match:
                output = output[:match.start('cmt')] + match.group('fmt').format(**stats) + output[match.end('cmt'):]
                response.content = output
        return response


class QuickPageStatsMiddleware(MiddlewareBase):
    """ Middleware de statistiques de performance (sortie console) """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Traiter la vue """
        self.view = view_func
        return None

    def __call__(self, request):
        """ Traiter la réponse """
        self.start = time()
        response = self.get_response(request)
        self.elapsed = time() - self.start
        sys.stderr.write("{view:<20} {total:>8.04f}s ".format(total=self.elapsed, view=self.view.__name__ if hasattr(self, 'view') else ""))
        return response


class SQLLogMiddleware(MiddlewareBase):
    """ Middleware répertoriant toutes les commandes SQL exécutées dans la page """

    def __call__(self, request):
        """ Traiter la réponse """
        response = self.get_response(request)
        time = sum([float(q['time']) for q in connection.queries])
        output = render_to_code(request, 'core/middleware/sqllog.html', {'sqllog': connection.queries, 'count': len(connection.queries), 'time': time})
        response.content += output.content
        return response


class QuickSQLLogMiddleware(MiddlewareBase):
    """ Middleware répertoriant toutes les commandes SQL exécutées (console) """

    def __call__(self, request):
        """ Traiter la réponse """
        response = self.get_response(request)
        time = sum([float(q['time']) for q in connection.queries])
        output = render_to_code(request, 'core/middleware/sqllog.html', {'sqllog': connection.queries, 'count': len(connection.queries), 'time': time})
        sys.stdout.write(output.content)
        sys.stdout.flush()
        return response


class MemoryUsageMiddleware(object):
    """ Middleware affichant l'utilisation mémoire des pages """

    def process_request(self, request):
        """ Traiter la requête """
        request._mem = psutil.Process(os.getpid()).get_memory_info()

    def process_response(self, request, response):
        """ Traiter la réponse """
        if getattr(request, 'user', False) and getattr(request, '_mem', False) and request.user.is_active and request.user.is_staff:
            mem = psutil.Process(os.getpid()).get_memory_info()
            diff = mem.rss - request._mem.rss
            output = render_to_string('core/middleware/memoryusage.html', {'usage': diff, 'start': request._mem.rss, 'end': mem.rss})
            response.content = response.content + output.encode('utf-8')
        return response
