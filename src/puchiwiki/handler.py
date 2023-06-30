#!/bin/env python3
# -*- coding: utf-8 -*-
### vim:set ts=4 sw=4 sts=0 fenc=utf-8:

###
### $Id: main.py 26 2018-03-16 03:25:31Z junichi $
###

import sys
import os
import re

import asyncio
import tornado

class MainHandler( tornado.web.RequestHandler ):
    def get( self ):
        self.write("Hello, world")

#EOF
