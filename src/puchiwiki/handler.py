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

class WikiHandler( tornado.web.RequestHandler ):

    def initialize(self, appSettings ):
        self.appSettings = appSettings

    def get( self, path ):

        log = getLogger( __name__ )

        self.write( "Hello, world<br>" )
        self.write( "<br>" )
        self.write( path )
        self.write( "<br>" )

        log.debug( "a" )

        try:
            self.write( str( self.settings ) )
        except Exception as e:
            log.exception( e )
#EOF
