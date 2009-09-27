# -*- coding: utf-8 -*-
# 
# Author: Jang-Ho Hwang <rath@xrath.com>
# Version: 1.0, since 2009/09/12
#
import re
import curses
import time

from utils import expand_to, length
import me2terminal

LOGO = (
"                  ___   __                      _             __",
"   ____ ___  ___ |__ \ / /____  _________ ___  (_)___  ____ _/ /",
"  / __ `__ \/ _ \__/ // __/ _ \/ ___/ __ `__ \/ / __ \/ __ `/ / ", 
" / / / / / /  __/ __// /_/  __/ /  / / / / / / / / / / /_/ / /  ", 
"/_/ /_/ /_/\___/____/\__/\___/_/  /_/ /_/ /_/_/_/ /_/\__,_/_/   ")
LOGO_W = 66
LOGO_H = 6

title = "Welcome to me2terminal!"
logo_window = None
login_window = None
label_id = "me2DAY ID: "

def _input(parent, w, y, x):
    curses.noecho()
    w.keypad(1)
    w.move(y, x)
    user_id = ''

    while True:
        ch = w.getch()
        if ch==curses.KEY_RESIZE:
            draw_login_window(parent)
            w = login_window 
            w.keypad(1)
            w.move(y, x)
            w.addstr(user_id, curses.A_UNDERLINE)
            continue

        if ch==curses.KEY_ENTER or ch==ord('\n') or ch==ord('\r'):
            if len(user_id)>2:
                break
            else:
                continue
        if ch in (curses.KEY_EXIT, 27):
            break
        if ch in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            # 시간이 남으면(?) left/right로 이동하고 insert 하는 것도 구현해보자. 
            # 물론 시간이 남을리는 없겠지만! 
            continue
        if ch==curses.KEY_BACKSPACE or ch==127:
            if len(user_id)==0:
                continue
            user_id = user_id[:-1]
            w.move(y, w.getyx()[1]-1)
            w.addch(' ', curses.A_UNDERLINE)
            w.move(y, w.getyx()[1]-1)
            continue
        if ch > 0 and ch < 256 and re.match("[A-Za-z0-9-_]", chr(ch)):
            if len(user_id) > 20:
                continue
            w.addch(ch, curses.A_UNDERLINE)
            user_id += chr(ch)
    curses.echo()
    w.keypad(0)
    return user_id 

def draw_login_window(parent):
    global login_window
    global logo_window

    if login_window:
        login_window.erase()
        login_window.refresh()
        del login_window
    if logo_window:
        logo_window.erase()
        logo_window.refresh()
        del logo_window

    parent.erase()
    me2terminal.paint_background(parent)
    parent.refresh()

    LINES = parent.getmaxyx()[0]
    COLS = parent.getmaxyx()[1]

    # logo window
    logo_y = (LINES-LOGO_H) / 2 - 4
    logo_window = curses.newwin(LOGO_H, LOGO_W, logo_y, (COLS-LOGO_W)/2)
    line = 1
    for logo_line in LOGO:
        logo_window.addstr(line, 1, logo_line)
        line += 1
    logo_window.refresh()

    # login window
    login_width, login_height = (42, 7)
    login_window = curses.newwin(
        login_height, login_width, 
        logo_y + LOGO_H + 1,
        (COLS-login_width)/2)
    login_window.border()
    login_window.addstr(1, 1, 
        expand_to(title, login_width-2), 
        curses.A_REVERSE | curses.A_BOLD)
    login_window.addstr(3, 4, label_id)
    login_window.addstr(' ' * (login_width-2-length(label_id)-8), curses.A_UNDERLINE)
    login_window.addstr(5, login_width-2-length("[Enter]"), "[Enter]")
    login_window.refresh()

def get_userid(parent):
    global logo_window
    global login_window

    draw_login_window(parent)

    user_id = _input(parent, login_window, 3, 4+length(label_id))
    # It's show time! Let's move both windows to the right corner.
    if len(user_id) > 2:
        ly, lx = logo_window.getbegyx()
        y, x = login_window.getbegyx()
        for i in range(1, 1): 
            newy = y+i*1
            newly = ly-i*1
            try:
                if newly <= 1: newly = 1
                logo_window.mvwin(newly, lx)
                if newy >= parent.getmaxyx()[0]-8: newy = parent.getmaxyx()[0]-8
                login_window.mvwin(newy, x)
            except:
                break

            me2terminal.paint_background(parent)
            parent.refresh()
            login_window.refresh()
            logo_window.refresh()

            time.sleep(0.09)
    else: 
        return ''

    logo_window.erase()
    login_window.erase()
    logo_window.refresh()
    login_window.refresh()

    me2terminal.paint_background(parent)
    parent.refresh()

    del logo_window
    del login_window

    return user_id


