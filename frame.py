#
# -*- coding: utf-8 -*-
# 
# Author: Jang-Ho Hwang <rath@xrath.com>
# Version: 1.0, since 2009/09/13
#
import curses

from me2day import me2API
import me2terminal, utils

stdscr = None

def main_loop(parent, user_id):
    stdscr = parent
    curses.noecho()

    show_tag = True
    api = me2API(user_id, '00000000', '6c82a48d9fd3fee0b2819251cc4fef98')

    # 좌/우 나 상/하 방향키를 이용하여 페이징을 처리할 수 있다. 
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK) # time
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK) # body
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK) # tag
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK) # metoo/comment count

    post_window = curses.newwin( curses.LINES-7, curses.COLS-4, 3, 1 )
    post_window.keypad(1)

    offset = 0
    prev_printed_line = 0

    cur_userid = user_id
    scope = 'all'
    scope_label = "미투데이"

    cur_post = None # for navigate, row. (post_id)
    cur_idx  = 0    # for navigate, column. (0, 1, 2, 3)
    cur_row = -1

    while True:
        parent.addstr(2, 3, "페이지를 읽어오고 있습니다. 잠시만 기다려주세요...", curses.A_NORMAL)
        parent.refresh()
        
        post_window.refresh()

        posts = api.get_posts({
            'offset': offset, 
            'count' : 20, 
            'scope' : scope
        }, cur_userid)
        
        parent.erase()
        me2terminal.paint_background(parent)
        parent.addstr(1, 2, "  %s님의 " % (cur_userid), 
            curses.A_REVERSE | curses.A_BOLD | curses.color_pair(4))
        parent.addstr("%s  " % scope_label,  
            curses.A_REVERSE | curses.A_BOLD | curses.color_pair(4))
        parent.addstr(1, curses.COLS-21, "%3d번째 글부터 표시" % (offset+1), curses.A_NORMAL)
        parent.refresh()

        post_window.erase()
        printed_line = show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx)

        quit = False
        while True:
            ch = post_window.getch()
            if ch==ord('1'): # my metoo
                cur_userid = user_id
                scope = 'all'
                scope_label = '미투데이'
                offset = 0
                break
            if ch==ord('2'): # all friends
                cur_userid = user_id
                scope = 'friend[all]'
                scope_label = '친구들은'
                offset = 0
                break
            if ch==ord('3'): # best friends
                cur_userid = user_id
                scope = 'friend[best]'
                scope_label = '관심친구들은'
                offset = 0
                break
            if ch==ord('4'): # close friends
                cur_userid = user_id
                scope = 'friend[close]'
                scope_label = '친한친구들은'
                offset = 0
                break
            if ch==ord('5'): # supporter friends
                cur_userid = user_id
                scope = 'friend[supporter]'
                scope_label = '지지자들은'
                offset = 0
                break

            if ch==ord('j') or ch==curses.KEY_DOWN: # move down 
                if cur_row < printed_line:
                    cur_row += 1
                    cur_post = posts[cur_row].id
                    post_window.erase()
                    show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx)
                pass
            if ch==ord('k') or ch==curses.KEY_UP: # move up 
                if cur_row > 0:
                    cur_row -= 1
                    cur_post = posts[cur_row].id
                    post_window.erase()
                    show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx)
                pass
            if ch==ord('h') or ch==curses.KEY_LEFT: # move left 
                if cur_idx > 0:
                    cur_idx -= 1
                    post_window.erase()
                    show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx)
                elif cur_idx==0 and cur_row > 0:
                    cur_row -= 1
                    cur_idx = 3
                    cur_post = posts[cur_row].id
                    post_window.erase()
                    show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx)
                    
            if ch==ord('l') or ch==curses.KEY_RIGHT: # move right
                if cur_idx < 3:
                    cur_idx += 1
                    post_window.erase()
                    show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx)
                elif cur_idx==3 and cur_row < printed_line:
                    cur_row += 1
                    cur_idx = 0
                    cur_post = posts[cur_row].id
                    post_window.erase()
                    show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx)

            if ch==ord('\n') or ch==ord(' '):
                # case cur_idx 
                # cur_post
                # 
                if cur_post and cur_idx==0: # go to selected user's me2day.
                    cur_userid = posts[cur_row].author.id.encode('utf-8')
                    cur_idx = 0; cur_row = -1
                    scope = 'all'
                    scope_label = '미투데이'
                    offset = 0
                    break
                if cur_post and cur_idx==1: # submit a metoo.
                    api.metoo({'post_id': cur_post})
                    break
                if cur_post and cur_idx==2: # view user list who clicked metoo.
                    persons = api.get_metoos({'post_id': cur_post}) 
                    show_metoos(persons, cur_row + 4)
                    post_window.erase()
                    show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx)

            if ch==ord('r'): # refresh current page.
                cur_idx = 0; cur_row = -1
                break
            if ch==ord('i'): # input mode.
                pass
            if ch==ord('p'): # previous page
                offset -= printed_line
                if offset < 0: offset = 0
                cur_idx = 0; cur_row = -1
                break
            if ch==ord('n'): # next page
                offset += printed_line
                cur_idx = 0; cur_row = -1
                break
            if ch==ord('q') or ch==27: # quit 
                quit = True
                break
        if quit:
            break

def show_posts(post_window, posts, offset, show_tag, cur_post, cur_idx):
    limit_y = post_window.getmaxyx()[0] - 1
    printed_line = 0

    selected = 0 # curses attributes for highlighted item.
    y = 0
    for post in posts:
        if y > limit_y: 
            break
        # 아이디 출력        
        x = 2 
        nick = post.author.nickname.encode('utf-8')
        nicklen = utils.length(nick)

        if cur_post==post.id and cur_idx==0: selected = curses.A_REVERSE
        else: selected = 0
        try:
            post_window.addstr(y, x+(10-nicklen), nick, 
                curses.A_UNDERLINE | curses.color_pair(1) | selected)
        except:
            pass

        # 내용
        x += 10 + 2
        content_w = post_window.getmaxyx()[1]-x-10
        body = post.body_as_text
        post_window.move(y, x)
        content_lines = 1

        for body_ch in body:
            post_window.addstr(body_ch.encode('utf-8'), curses.A_NORMAL | curses.color_pair(4))
            if post_window.getyx()[1]+2 >= x+content_w:
                if y+content_lines > limit_y:
                    break
                post_window.move(y+content_lines, x)
                content_lines += 1

        # 날짜 (UTC 문제 해결할 것)
        if y+1 > limit_y: 
            break
        post_window.move(y+1, x-10-1)
        post_window.addstr("%2d일%02d:%02d" % (post.date.day, post.date.hour, post.date.minute), curses.A_NORMAL | curses.color_pair(3)) 
        
        if show_tag:
            # 태그 
            if len(post.tags) > 0:
                if y+content_lines > limit_y:
                    break
                post_window.move(y+content_lines, x)
                tags = "# %s" % (' '.join(post.tags))
                for tag_ch in tags:
                    post_window.addstr(tag_ch.encode('utf-8'), curses.A_DIM | curses.color_pair(5))
                    if post_window.getyx()[1]+2 >= x+content_w:
                        break # 긴 태그는 가볍게 무시
                content_lines += 1

        # 미투수 출력, 미투하기 링크 출력
        x += content_w
        post_window.move(y, x)

        if cur_post==post.id and cur_idx==1: selected = curses.A_REVERSE
        else: selected = 0
        post_window.addstr("metoo",     
            curses.A_NORMAL | curses.color_pair(2) | selected)
        if cur_post==post.id and cur_idx==2: selected = curses.A_REVERSE
        else: selected = 0
        post_window.addstr(" ")
        post_window.addstr("%2d" % (post.metoo_count), 
            curses.A_NORMAL | curses.color_pair(6) | selected)
        if y+1 > limit_y:
            break
        post_window.move(y+1, x+1)
        post_window.addstr( "댓글 ", curses.A_NORMAL)
        if cur_post==post.id and cur_idx==3: selected = curses.A_REVERSE
        else: selected = 0
        post_window.addstr("%2d" % (post.comment_count), 
            curses.A_UNDERLINE | curses.color_pair(6) | selected)

        # metoo, comment 출력을 위해 최소 라인을 2줄로 맞춤.
        if content_lines==1:    
            content_lines = 2
        y += content_lines 
        printed_line += 1

    post_window.refresh()
    return printed_line

def show_metoos(persons, window_y):
    cols = 40 + 4 
    rows = len(persons)/4 + 1 + 2
    
    w = curses.newwin(rows, cols, (curses.LINES-rows)/2, (curses.COLS-cols)/2)
    w.border()
    x = 3
    y = 1
    for i in range(len(persons)):
        w.addstr(y, x, persons[i][0].nickname.encode('utf-8'), 
            curses.A_UNDERLINE | curses.color_pair(1))
        x += 10
        if (i+1)%4==0:
            y += 1
            x = 3
        
    w.getch()
    w.erase()
    w.refresh()

