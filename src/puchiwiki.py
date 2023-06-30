#!/bin/env python3
# -*- coding: utf-8 -*-
### vim:set ts=4 sw=4 sts=0 fenc=utf-8:

###
### $Id: main.py 26 2018-03-16 03:25:31Z junichi $
###

import sys
import os
import os.path

if __name__ == "__main__":

    from puchiwiki import webserver

    webserver.run( os.path.dirname( os.path.abspath( __file__ ) ) )

#EOF
