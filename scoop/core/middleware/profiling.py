# coding: utf-8
import cProfile
import logging
import os
import re
import sys
from operator import add
from time import time

import psutil
from django.conf import settings
from django.db import connection
from django.template.context import RequestContext
from django.template.loader import render_to_string

from scoop.core.util.django.templateutil import render_to_code


logger = logging.getLogger(__name__)


class ProfilerMiddleware(object):
    """ Middleware de profilage """
    # Constantes
    HTML_SIGNAL = u"<!-- debug -->"

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """ Traiter la vue """
        if settings.DEBUG and request.user.is_staff:
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        """ Traiter la réponse """
        if settings.DEBUG and request.user.is_staff and hasattr(self, 'profiler'):
            self.profiler.create_stats()
            stats = self.profiler.getstats()
            stats = sorted(stats, key=lambda k: -k.inlinetime)
            total_time = reduce(lambda x, y: x + y.inlinetime, stats, 0)
            total_calls = reduce(lambda x, y: x + y.callcount, stats, 0)
            insert_pos = unicode(response.content, 'utf-8').rfind(ProfilerMiddleware.HTML_SIGNAL)
            if insert_pos != -1:
                output = render_to_string('core/middleware/profiling.html', {'stats': stats, 'total_time': total_time, 'total_calls': total_calls}, context_instance=RequestContext(request))
                response.content = response.content.decode('utf-8').replace(ProfilerMiddleware.HTML_SIGNAL, output, 1)
            elif 'profile' in request.GET:
                output = render_to_string('core/middleware/profiling.html', {'stats': stats, 'total_time': total_time, 'total_calls': total_calls}, context_instance=RequestContext(request))
                response.content += output
        return response


class PageStatsMiddleware(object):
    """ Middleware de statistiques de performance de la page """

    def process_request(self, request):
        """ Traiter la requête """
        connection.use_debug_cursor = True
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
            regexp = re.compile(r'(?P<cmt><!--\s*STATS:(?P<fmt>.*?)-->)')
            match = regexp.search(output)
            if match:
                output = output[:match.start('cmt')] + match.group('fmt').format(**stats) + output[match.end('cmt'):]
                response.content = output
        return response


class QuickPageStatsMiddleware(object):
    """ Middleware de statistiques de performance (sortie console) """

    def process_request(self, request):
        """ Traiter la requête """
        self.start = time()
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Traiter la vue """
        self.view = view_func
        return None

    def process_response(self, request, response):
        """ Traiter la réponse """
        self.elapsed = time() - self.start
        sys.stderr.write("{view:<20} {total:>8.04f}s ".format(total=self.elapsed, view=self.view.__name__ if self.view else ""))
        return response


class SQLLogMiddleware(object):
    """ Middleware répertoriant toutes les commandes SQL exécutées dans la page """

    def process_response(self, request, response):
        """ Traiter la réponse """
        time = sum([float(q['time']) for q in connection.queries])
        output = render_to_code(request, 'core/middleware/sqllog.html', {'sqllog': connection.queries, 'count': len(connection.queries), 'time': time})
        response.content += output.content
        return response


class QuickSQLLogMiddleware(object):
    """ Middleware répertoriant toutes les commandes SQL exécutées (console) """

    def process_response(self, request, response):
        """ Traiter la réponse """
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
