# -*- coding: utf-8 -*-
# 
# Author: Jang-Ho Hwang <rath@xrath.com>
# Version: 1.0, since 2009/09/12
#

def length(str): return len(str.decode('utf-8').encode('euc-kr'))
def expand_to(str, len, pad_char=' '): 
    remain = len - length(str)
    pad = remain / 2 
    ret = "%s%s%s" % (pad_char*pad, str, pad_char*pad)
    if remain%2==1: ret = ret + pad_char
    return ret
