# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.apps import AppConfig


class MyConfig(AppConfig):
    name = 'dashboard.home'
    label = 'apps_home'

    def ready (self):
        import dashboard.home.signals

    


