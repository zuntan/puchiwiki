#!/bin/env python3
# -*- coding: utf-8 -*-
### vim:set ts=4 sw=4 sts=0 fenc=utf-8:

###
### $Id: main.py 26 2018-03-16 03:25:31Z junichi $
###

import sys
import os
import os.path

import asyncio
import tornado

from . import handler

from datetime import datetime, timezone, timedelta

import logging.config
from logging import getLogger

import configparser

CONFFILE_ENCODING = "utf8"

##
def setupLogger( logging_conf_param ):

    logging_conf = configparser.ConfigParser( interpolation=configparser.ExtendedInterpolation() )
    logging_conf_target = logging_conf_param.split(':')
    logging_conf_loaded = logging_conf.read( logging_conf_target, encoding=CONFFILE_ENCODING )

    logging.config.fileConfig( logging_conf )

    return ( logging_conf_target, logging_conf_loaded )

async def main( svr_port, svr_addr, appSettings ):

    log = getLogger( __name__ )

    log.debug( appSettings['basedir'] + "data/static".replace("/", os.path.sep) )

    application = tornado.web.Application(
            [
                ( r"/",                 tornado.web.RedirectHandler, {"url": "/wiki/"} )
            ,   ( r"/wiki/(.*)",        handler.WikiHandler, { "appSettings": appSettings } )
            ,   ( r"/static/(.*)",      tornado.web.StaticFileHandler, { "path": appSettings['static_path'] } )
            ]
        ,   settings = appSettings
    )



    try:
        server = tornado.httpserver.HTTPServer( application, xheaders=True )
        server.listen( svr_port, svr_addr )

        await asyncio.Event().wait()

    except asyncio.exceptions.CancelledError as e:
        log.info( "CancelledError" )

    except Exception as e:
        log.exception( e )

    except:
        log.exception( "Unexpected error" )

def run(  _basedir = None ):

    if not _basedir:
        _basedir = os.path.abspath( os.getcwd() )

    import tornado.options

    tornado.options.define( "logging_conf", default="logging.conf:logging_local.conf",      help="" )
    tornado.options.define( "puchiwiki_conf",default="puchiwiki.conf:puchiwiki_local.conf", help="" )

    tornado.options.parse_command_line()

    opt = tornado.options.options

    ( _logging_conf_target, _logging_conf_loaded ) = setupLogger( opt.logging_conf )

    log = getLogger( __name__ )

    ### settings start ###

    _app_conf = configparser.ConfigParser( interpolation=configparser.ExtendedInterpolation() )
    _app_conf_target = opt.puchiwiki_conf.split(':')
    _app_conf_loaded = _app_conf.read( _app_conf_target, encoding=CONFFILE_ENCODING )

    _app_conf.set( 'global', 'basedir', _basedir )

    svr_port = _app_conf.getint( 'global', 'svr_port',   fallback=8880 )
    svr_addr = _app_conf.get( 'global', 'svr_addr',   fallback='' )

    app_date_dt_disp = ""
    app_date_tm_disp = ""
    app_date_tz_disp = ""

    try:
        d = datetime.strptime( re.sub(r'\..*', "+0000", _svn_commitdate ), "%Y-%m-%dT%H:%M:%S%z" ).astimezone()
        app_date_dt_disp = d.strftime( "%Y-%m-%d" )
        app_date_tm_disp = d.strftime( "%H:%M:%S" )
        app_date_tz_disp = d.strftime( "%z" )
    except Exception as e:
        log.exception( e )

    _app_conf.set( 'global', 'app_date_dt_disp', app_date_dt_disp )
    _app_conf.set( 'global', 'app_date_tm_disp', app_date_tm_disp )
    _app_conf.set( 'global', 'app_date_tz_disp', app_date_tz_disp )

    log.info( "*** start ***" )

    log.info( "svr_port            :%d", svr_port )
    log.info( "svr_addr            :%s", svr_addr )

    log.info( "basedir             :%s", _basedir )
    log.info( "logging_conf        :%s", _logging_conf_target )
    log.info( "logging_conf_loaded :%s", _logging_conf_loaded )
    log.info( "app_conf            :%s", _app_conf_target )
    log.info( "app_conf_loaded     :%s", _app_conf_loaded )

    appSettings = dict(
        debug                   = _app_conf.getboolean( 'tornadoapp', 'debug',                     fallback=False )
    ,   autoreload              = _app_conf.getboolean( 'tornadoapp', 'autoreload',                fallback=False )
    ,   compiled_template_cache = _app_conf.getboolean( 'tornadoapp', 'compiled_template_cache',   fallback=True )
    ,   static_hash_cache       = _app_conf.getboolean( 'tornadoapp', 'static_hash_cache',         fallback=True )
    ,   serve_traceback         = _app_conf.getboolean( 'tornadoapp', 'serve_traceback',           fallback=False )

    ,   compress_response       = _app_conf.get( 'tornadoapp', 'compress_response', fallback=True )

    ,   cookie_secret           = _app_conf.get( 'global', 'cookie_secret' )
    ,   xsrf_cookies            = True

    ,   template_path           = os.path.join( _basedir ,  "templates" )
    ,   autoescape              = 'xhtml_escape'
    ,   template_whitespace     = _app_conf.get( 'tornadoapp', 'template_whitespace',   fallback='all' )

    ,   static_path             = os.path.join( _basedir ,  "static" )

    ,   app_conf                = _app_conf
    ,   basedir                 = _basedir
    )

    ### settings end ###

    log.info( "server start" )

    try:
        asyncio.run( main( svr_port, svr_addr, appSettings ) )

    except KeyboardInterrupt as e:
        log.info( "KeyboardInterrupt" )

    except Exception as e:
        log.exception( e )

    except:
        log.exception( "Unexpected error" )

    log.info( "server shutdown" )

#EOF
