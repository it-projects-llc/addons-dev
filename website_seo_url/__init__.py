# -*- coding: utf-8 -*-
from . import models


def post_load():
    from . import ir_http
