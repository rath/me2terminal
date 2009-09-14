# -*- coding: utf-8 -*-
from me2day import me2API

if __name__=='__main__': 
    api = me2API('rath', '', '_application_key_') 
    for f in api.get_friends():
        print "%s(%s)" % (f.id, f.nickname)

#    api.create_comment({'post_id': 'p2mjxx', 'body': 'just for test'})

    for p in api.get_posts({'scope': 'friend[close]', 'count': 20}):
        print p.id + ", " + p.author.nickname + ": " + p.body_as_text 

        for metoo in api.get_metoos({'post_id': p.id}):
            person, date = metoo
            print date + ", " + person.nickname

        for comment in api.get_comments({'post_id': p.id}):
            print "  %s, %s: %s" % (comment.id, comment.author.nickname, comment.body)

    api.noop()
