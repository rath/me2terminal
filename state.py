#
# -*- coding: utf-8 -*-
# 
# Author: Jang-Ho Hwang <rath@xrath.com>
# Version: 1.0, since 2009/09/27
#

class State:
    def __init__(self):
        self.offset = 0
        self.cur_userid = None
        self.scope = 'all'
        self.scope_label = '미투데이'
        self.cur_post = None # for navigate, row. (post_id)
        self.cur_idx = 0     # for navigate, column. (0, 1, 2, 3)
        self.cur_row = -1

        self.printed_line = 0
        self.posts = []

    def reset(self):
        self.offset = 0        
        self.cur_userid = None
        self.scope = 'all'
        self.scope_label = '미투데이'
        self.cur_post = None
        self.cur_idx = 0
        self.cur_row = -1

        self.printed_line = 0
        self.posts = []

    def go_me2day_id(self, me2day_id):
        self.reset()
        self.cur_userid = me2day_id

    def is_me2day_id(self):
        return self.cur_post and self.cur_idx==0

    def is_metoo_action(self):
        return self.cur_post and self.cur_idx==1
    
    def is_metoo_count(self):
        return self.cur_post and self.cur_idx==2

    def is_comment_count(self):
        return self.cur_post and self.cur_idx==3

    def current_post(self):
        return self.posts[self.cur_row]

    def set_scope(self, scope, scope_label):
        self.scope = scope
        self.scope_label = scope_label
        
    def refresh(self):
        self.cur_idx = 0
        self.cur_row = -1

    def move_down(self):
        if self.cur_idx==2:
            self.cur_idx += 1
        elif self.cur_idx==3 and self.cur_row < self.printed_line:
            self.cur_idx -= 1
            self.cur_row += 1
            self.cur_post = self.posts[self.cur_row].id
        elif self.cur_row < self.printed_line:
            self.cur_row += 1
            self.cur_post = self.posts[self.cur_row].id

    def move_up(self): 
        if self.cur_idx==3:
            self.cur_idx -= 1
        elif self.cur_idx==2 and self.cur_row > 0:
            self.cur_idx += 1
            self.cur_row -= 1
            self.cur_post = self.posts[self.cur_row].id
        elif self.cur_row > 0:
            self.cur_row -= 1
            self.cur_post = self.posts[self.cur_row].id

    def move_left(self):
        if self.cur_idx > 0:
            self.cur_idx -= 1
            return True
        return False

    def move_right(self):
        if self.cur_idx < 3:
            self.cur_idx += 1
            return True
        return False

    def go_previous_page(self):
        self.offset -= self.printed_line
        if self.offset < 0: 
            self.offset = 0
        self.cur_idx = 0
        self.cur_row = -1
    
    def go_next_page(self):
        self.offset += self.printed_line
        self.cur_idx = 0
        self.cur_row = -1
