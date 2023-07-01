#!/bin/env python3
# -*- coding: utf-8 -*-
### vim:set ts=4 sw=4 sts=0 fenc=utf-8: ### unicode ★ marker

###
### $Id: util.py 108 2018-05-08 11:52:44Z junichi $
###

"""
汎用の関数・クラス
"""

import sys
import os
import os.path
import io
import re
import enum
import random
import string
import json

from datetime import datetime, date, timedelta

import traceback

from logging import getLogger, DEBUG
##
log = getLogger( __name__ )

##
def objectId( obj ):
    """
    str( type( obj ) ) と同等の文字列を生成します。

    :param object obj: オブジェクトの参照

    この実装はいわゆるサンプル実装となります。この関数を直接使うことは無いと思います。

    各オブジェクトの ``def __repr__( self ):`` 等の実装で、参考としてください。
    """
    return '%s.%s object at %s' % ( obj.__module__, type( obj ).__name__, hex( id( obj ) ) )

##
def classId( clazz ):

    return '%s.%s class at %s' % ( clazz.__module__, clazz.__qualname__, hex( id( clazz ) ) )

##
class DefaultReprBehavior():
    """
    ``def __repr__( self ):`` にて、str( type( obj ) ) と同等の文字列を返すクラスの実装サンプル
    """

    ##
    def __repr__( self ):
        """
        ``objectId( self )`` を返します。
        """
        return '<%s>' % ( objectId( self ), )
##
def noneStr( value ):
    """
    値が None の場合、空文字列を返し、それ以外の場合は、そのまま返します

    :param str value: None または 文字列
    """
    return '' if value is None else str( value )

##
def strNone( value ):
    """
    値が None または 空文字列の場合、None 返し、それ以外の場合は、str関数の返値を返します

    :param str value: None または 文字列
    """
    return None if value is None or str( value ).strip() == '' else str( value )

##
def datetimeToStrDisp( value ):
    """
    与えられた datetime値から、画面表示用 ``yyyy/mm/dd hh:mm:ss`` 形式の文字列を返します。

    :param datetime value: None または datetime 値
    """
    if value != None:
        return value.strftime( '%Y/%m/%d %H:%M:%S' )

    return ''

##
def datetimeToStrIso( value ):
    """
    与えられた datetime値から、内部データ用 ``yyyy-mm-ddThh:mm:ss`` 形式の文字列を返します。

    :param datetime value: None または datetime 値
    """
    if value != None:
        return value.isoformat( timespec='seconds' )

    return ''

##
def strToDatetime( value ):
    """
    与えられた日付文字列値から、datetime値に変換します。

    :param str value: None または 日付文字列
    :return: datetime値 変換できなかった場合は、None
    :rtype: datetime または None

    入力可能な日付文字列は以下の通りです。

    * ``%Y-%m-%dT%H:%M:%S``
    * ``%Y-%m-%d %H:%M:%S``
    * ``%Y/%m/%d %H:%M:%S``
    * ``%Y-%m-%dT%H:%M:%S.%f``
    * ``%Y-%m-%d %H:%M:%S.%f``
    * ``%Y/%m/%d %H:%M:%S.%f``

    """

    if isinstance( value, datetime ):
        return value

    for fmt in (
        '%Y-%m-%dT%H:%M:%S'
    ,   '%Y-%m-%d %H:%M:%S'
    ,   '%Y/%m/%d %H:%M:%S'
    ,   '%Y-%m-%dT%H:%M:%S.%f'
    ,   '%Y-%m-%d %H:%M:%S.%f'
    ,   '%Y/%m/%d %H:%M:%S.%f'
    ,   '%Y-%m-%d'
    ,   '%Y/%m/%d'
    ):
        try:
            return datetime.strptime( value, fmt )
        except:
            pass

    return None

##
def timedeltaToStr( value ):
    """  与えられた timedelta 値から、画面表示用 ``[D day[s], ]HH:MM:SS`` 形式の文字列を返します。

    :param datetime.timedelta value: 経過時間

    str( timedelta ) だと、 ``[D day[s], ][H]H:MM:SS[.UUUUUU]`` だったので、ちょっと気に入らなかったので作りました。
    """

    ret = ""

    if value.days != 0:

        ret = "%d day" % ( value.days, )

        if abs( value.days ) != 1:
            ret += "s"

        ret += ", "


    ( h, m ) = divmod( value.seconds, 3600 )
    ( m, s ) = divmod( m, 60 )

    ret += "%02d:%02d:%02d" % ( h, m, s )

    return ret

##
def findEnum( enumClass, enumOrKeyOrValue ):
    """
    文字列から enum の メンバー値に変換します。

    :param enum enumClass: enum.Enum からの派生クラス
    :param any enumOrKeyOrValue: 変換したい値
    :return: enumClass のメンバー値
    :exception KeyError: 変換できなかった場合は、 を送出

    例::

        >>> import enum
        >>> import util
        >>> class MY_ENUM( enum.Enum ):
        ...     HOGE = enum.auto()
        ...     FUGA = enum.auto()
        ...
        >>> util.findEnum( MY_ENUM, 'FUGA' )
        <MY_ENUM.FUGA: 2>

    """

    if isinstance( enumOrKeyOrValue, enumClass ):
        return enumOrKeyOrValue

    try:
        return enumClass( enumOrKeyOrValue )    ## raise ValueError

    except ValueError as e:
        pass

    return enumClass[ enumOrKeyOrValue ]        ## raise KeyError

##
def _getStackSigFormat( stack ):
    ( filename, lineno, name, line ) = stack
    return "%s:%d - %s " % ( os.path.basename( filename ), lineno, name )

##
def getStackSig():
    """
    トレースバック情報から、呼び出し元関数の、ファイル名・行番号・名称、からなる文字列を生成します。
    """
    return _getStackSigFormat( traceback.extract_stack( limit=2 )[ 0 ] )

##
def getStackSigParent():
    """
    トレースバック情報から、呼び出し元関数のさらに１つ上の呼び出し元関数の、ファイル名・行番号・名称、からなる文字列を生成します。
    """
    return _getStackSigFormat( traceback.extract_stack( limit=3 )[ 0 ] )

##
def dynLoadClass( name ):

    import importlib

    dot = name.rfind( '.' )
    mod_name = name[ :dot ]
    cls_name = name[ dot+1:]

    log.debug( 'loadClass mod:%s cls:%s', mod_name, cls_name )

    mod = importlib.import_module( mod_name )
    cls = getattr( mod, cls_name )

    return cls

##
class NoMissingDict( dict ):
    """
    エントリーが登録されていないキーに対する取得があった場合、空文字列を返す dict です。
    """

    ##
    def __missing__( self, key ):
        """
        空文字列を返します。
        """
        return ""

##
class DotAccessible( object ):
    """
    辞書に対して、プロパティ記述によるバリュー値の取得ができるようにするラッパーです。

    ``obj['hoge']`` と同様、``obj.hoge`` でも値が取得できます。

    また、その時のバリュー値が、tuple,list,dict であったばあいは、その バリュー値 にたいしても自動でラップします。
    よって、以下のような記述が可能となります。

    ``obj.fuga[0].hohe`` ``obj.muho.buha`` ``obj.aaa.bbb.ccc``

    """

    ##
    def __init__( self, obj ):
        self.obj = obj

    ##
    def __getitem__(self, i):
        return self.wrap( self.obj[ i ] )

    ##
    def __getslice__(self, i, j):
        return map( self.wrap, self.obj.__getslice__( i, j ) )

    ##
    def __getattr__( self, key ):
        if isinstance( self.obj, dict ):
            try:
                v = self.obj[ key ]
            except KeyError:
                v = self.obj.__getattribute__( key )
        else:
            v = self.obj.__getattribute__( key )

        return self.wrap( v )

    ##
    def __len__( self ):
        return len( self.obj )

    ##
    def __iter__( self ):
        for i in self.obj:
            yield self.wrap( i )

    ##
    def __contains__( self, item ):
        return self.obj.__contains__( item )

    ##
    def wrap( self, v ):
        if isinstance( v, ( dict, list, tuple ) ):
            return self.__class__( v )
        return v


##
class DotAccessibleWithNMD( DotAccessible ):
    """
    辞書に対して、プロパティ記述によるバリュー値の取得ができるようにするラッパーです。

    ``DotAccessible`` と同様ですが、 ``NoMissingDict`` と協調して、存在しないキーに対しては、空文字が返る実装となります。
    （ WithNMD は、 with NoMissingDict の略です ）
    """

    ##
    def __init__( self, obj ):
        if isinstance( obj, dict ) and not isinstance( obj, NoMissingDict ):
            obj = NoMissingDict( obj )
        super().__init__( obj )

    ##
    def wrap( self, v ):
        if isinstance( v, NoMissingDict ):
            return self.__class__( v )
        return super().wrap( v )

##
class PagenationInfo():

##
    def __init__( self, _cur_page, _max_page, _view_pages ):
        self.cur_page = _cur_page
        self.max_page = _max_page
        self.view_pages_half = int( _view_pages / 2 )
        self.prev_page = None
        self.next_page = None
        self.prev_dot  = None
        self.next_dot  = None
        self.first_page = None
        self.last_page = None

        if _max_page > ( self.view_pages_half * 2 + 1 ):
            self.prev_page = self.cur_page - 1 if self.cur_page > 1 else None
            self.next_page = self.cur_page + 1 if self.cur_page >= 1 and self.cur_page < self.max_page else None
            self.prev_dot  = True if self.cur_page - self.view_pages_half > 1 else None
            self.next_dot  = True if self.cur_page + self.view_pages_half < self.max_page else None
            self.first_page = 1 if self.prev_dot else None
            self.last_page = self.max_page if self.next_dot else None
            st = self.cur_page - self.view_pages_half
            if st < 1:
                st = 1
            if st > self.max_page - ( self.view_pages_half * 2 ):
                st = self.max_page - ( self.view_pages_half * 2 )
            self.pages = tuple( range( st, st + ( self.view_pages_half * 2 + 1 ) ) )

        else:
            self.pages = tuple( range( 1, _max_page + 1 ) )

    ##
    def __repr__( self ):
        part = []
        if self.first_page:
            part.append( "F(%d)" % ( self.first_page, ) )
        if self.prev_page:
            part.append( "P(%d)" % ( self.prev_page, ) )
        if self.prev_dot:
            part.append( "..." )
        for x in self.pages:
            if x == self.cur_page:
                part.append( "(%d)" % ( x, ) )
            else:
                part.append( "%d" % ( x, ) )
        if self.next_dot:
            part.append( "..." )
        if self.next_page:
            part.append( "N(%d)" % ( self.next_page, ) )
        if self.last_page:
            part.append( "L(%d)" % ( self.last_page, ) )
        return ' '.join( part )

# EOT
