#!/bin/env python3
# -*- coding: utf-8 -*-
### vim:set ts=4 sw=4 sts=0 fenc=utf-8:

###
### $Id: main.py 26 2018-03-16 03:25:31Z junichi $
###

import sys
import os
import re
import os.path

from logging import getLogger

import asyncio
import tornado

from . import util

class WikiHandler( tornado.web.RequestHandler ):

    def initialize(self, app_settings ):
        self._app_conf      = app_settings['app_conf']
        self._app_render    = dict( app_settings['app_render'] )
        self._errors        = []
        self._infos         = []

    def get_template_namespace( self ):

        arg = dict(
            app_render  = self._app_render
        ,   errors      = self._errors
        ,   infos       = self._infos
        )

        namespace = dict( super().get_template_namespace() )
        namespace.update( arg = util.DotAccessibleWithNMD( arg ) )

        return namespace

    def get( self, path ):

        log = getLogger( __name__ )

        try:
            self.render('wiki.html' )

        except Exception as e:
            log.exception( e )
#EOF
