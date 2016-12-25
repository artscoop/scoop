# coding: utf-8
import psutil
from admin_tools.dashboard.modules import DashboardModule
from django.core.cache import cache
from django.shortcuts import render
from django.template.loader import render_to_string

from scoop.core.models.recorder import Record
from scoop.core.util.stream.fileutil import get_free_disk_space


PROCESS_NAMES = ['gunicorn', 'django', 'celery']
try:
    pids = psutil.pids()
    processes = [psutil.Process(pid) for pid in pids if [True for name in PROCESS_NAMES if name in psutil.Process(pid).name]]
except:
    processes = []


class SystemModule(DashboardModule):
    """ Dashboard admin-tools de statistiques système """
    pre_content = ""
    title = "System information"

    def init_with_context(self, context):
        """ Initialiser le contenu du dashboard """
        output = cache.get('dashboard.sysinfo', None)
        if not output:
            cpu_usage = psutil.cpu_percent(interval=0, percpu=True)
            memuse = psutil.virtual_memory()._asdict()
            memory_usage_mb = {'total': memuse['total'] / 1024.0 ** 3, 'used': memuse['used'] / 1024.0 ** 3, 'free': memuse['free'] / 1024.0 ** 3,
                               'percent': memuse['percent'],
                               'programs': (memuse['total'] - memuse['available']) / 1024.0 ** 3}
            disk_stats = {'free': get_free_disk_space() / 1024.0 ** 3, 'percent': get_free_disk_space(percent=True)}
            if disk_stats['percent'] <= 100:
                disk_stats['status'] = 'success'
            if disk_stats['percent'] <= 50:
                disk_stats['status'] = 'warning'
            if disk_stats['percent'] <= 20:
                disk_stats['status'] = 'danger'
            for process in processes:
                process.cpu_percent = process.get_cpu_percent(interval=0)
            output = render_to_string("core/dashboard/system.html",
                                      {'cpu_usage': cpu_usage, 'memory': memory_usage_mb, 'disk': disk_stats, 'processes': processes})
            cache.set('dashboard.sysinfo', output, 5)
        self.pre_content = output

    def is_empty(self):
        """ Renvoyer si le dashboard est vide """
        return False


class RecordModule(DashboardModule):
    """ Dashboard admin-tools des activités enregistrées """
    pre_content = ""
    title = "Activity history"

    def init_with_context(self, context):
        """ Initialiser le contenu du dashboard """
        records = Record.objects.all().order_by('-id')
        output = render(context['request'], "core/dashboard/recorder.html", {'records': records}).content
        self.pre_content = output

    def is_empty(self):
        """ Renvoyer si le dashboard est vide"""
        return False
