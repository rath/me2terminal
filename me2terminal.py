#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# 
# Author: Jang-Ho Hwang <rath@xrath.com>
# Version: 1.0, since 2009/09/12
#
import curses
import locale

import login
import frame

def paint_background(window):
    window.border()
    copyright = " me2terminal by rath "
    window.addstr(
        curses.LINES-1, curses.COLS-len(copyright)-3, 
        copyright, curses.A_NORMAL)

if __name__=='__main__':
    locale.setlocale(locale.LC_ALL, '')
    stdscr = curses.initscr()
    curses.start_color()
    curses.raw()

    # Draw background
    paint_background(stdscr)
    stdscr.refresh()

    try:
        # Print logo and gather username in me2day.net.
        user_id = login.get_userid(stdscr)
        if len(user_id) > 2: # let's go to the me2day.net.
            frame.main_loop(stdscr, user_id)
             
    finally:
       curses.endwin() 


