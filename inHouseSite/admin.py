# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Player, Document
# Register your models here.

admin.site.register(Player)
admin.site.register(Document)