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

INDEX_FORMAT = re.compile( r"^\s*([^\s]+)\s+([^\s]+)" );

class WikiHandler( tornado.web.RequestHandler ):

    def initialize(self, app_settings ):
        self._app_conf      = app_settings['app_conf']
        self._app_render    = dict( app_settings['app_render'] )
        self._errors        = []
        self._infos         = []

        self._basedir       = app_settings['basedir']
        self._lock          = app_settings['lock']

    def get_template_namespace( self ):

        arg = dict(
            app_render  = self._app_render
        ,   errors      = self._errors
        ,   infos       = self._infos
        )

        namespace = dict( super().get_template_namespace() )
        namespace.update( arg = util.DotAccessibleWithNMD( arg ) )

        return namespace

    async def get_content( self, path ):

        ret = ( False, None )

        log = getLogger( __name__ )

        path_wiki = os.path.join( self._basedir, "data", "wiki" )

        path_target = ""

        try:

            async with self._lock:
                if path == "":
                    path_target = "_w_root.txt"
                else:

                    with open( os.path.join( path_wiki, "_w_index.txt" ), "r", encoding="utf-8" ) as f_idx:
                        for ln in f_idx:
                            m = INDEX_FORMAT.match( ln )
                            if m:
                                if m[2] == path:
                                    path_target = m[1]
                                    break


                if path_target != "":
                    cont = ""

                    with open( os.path.join( path_wiki, path_target ), "r", encoding="utf-8" ) as f_cont:
                        for ln in f_cont:
                            cont += ln

                    ret = ( True, cont )

        except Exception as e:
            log.fatal( e )

        return ret

    async def get( self, path ):

        log = getLogger( __name__ )

        log.debug( path )

        try:

            ( ok, cont ) = await self.get_content( path )

            if ok:
                await self.render( 'wiki.html', **dict( cont = cont ) )
            else:
                await self.render( 'not_found.html' )

        except Exception as e:
            log.exception( e )
#EOF
