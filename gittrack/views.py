import sys
# from django.http import Http404
# from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse#, HttpResponseRedirect
# from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, render_to_response
import datetime
from issue import *
try:
    import config
except:
    config = None

DAYWIDTH = 180
CARDWIDTH = 300

static_context = {
    'images': 'static/images/',
    'scripts': 'static/scripts/',
}

def home(request):
    context = dict(static_context)
    user = request.GET['user']
    pw = request.GET['pw']
    repo = request.GET['repo']
    context['repo'] = repo
    if 'milestone' in request.GET:
        mil = request.GET['milestone']
    else:
        return HttpResponse("Must specify a milestone")

    #very basic security
    print "PATH:", sys.path
    if config and user in config.user:
        if pw in config.user[user]['pw']:
            pw = config.user[user]['pw'][pw]
        else:
            return HttpResponse("bad password")
        user = config.user[user]['user']
        print "DEBUG using alias", user
    else:
        print "DEBUG not using alias, config=", config

    owner = request.GET['owner'] if 'owner' in request.GET else user
    context['owner'] = owner
        
#     print ("REPO:", repo, "OWNER:", owner, "USER:", user, "MILESTONE:", mil)
    issues = get_issues(user, pw, repo, owner, mil)
    if type(issues) != list:
        return HttpResponse(issues)
    parse_issues(issues)
#     for iss in issues:
#         print "ISSUE:", iss.bigrepr()
    crit, path = compute_crit(issues)
#     print "critical path days: %.2f path: %s" % (crit, ["%d|%.2f" % (x.num, x.estimate) for x in path])

    if not issues:
        return HttpResponse("no issues found")

    #create date column
    start = issues[0].mil_start
    due = issues[0].mil_due
    if due and not start:
        start = due - datetime.timedelta(days=7)
    elif start and not due:
        due = start + datetime.timedelta(days=7)
    elif not start and not due:
        return HttpResponse("milestone needs a start and due date.  Add start date as ST:2011-1-1")
#     print "start date:", start, "due date:", due
    days = []
    today = start
    now = datetime.datetime.now()
    nowday = tzlocal.get_localzone().localize(datetime.datetime(now.year, now.month, now.day)).astimezone(pytz.utc)  #yep, 'tis a mouthful
#     print "LOCAL:", tzlocal.get_localzone()
#     print "START:", start 
#     print "NOW:", now 
#     print "NOWDAY:", nowday 
#     print "DUE:", due
    while today <= due:
        day = {}
        day['date'] = today.strftime("%Y-%m-%d")
        day['dow'] = today.strftime("%A")[:3]
        if today < nowday:
            day['color'] = "#bbb"
        else:
            day['color'] = "#ddd"
        days.append(day)
        today += datetime.timedelta(days = 1)
        #everybody's working 4 the wkend
        if today.strftime("%A") == 'Saturday':
            today += datetime.timedelta(days = 2)            
#     print "DAYS:", days
    context['days'] = days
    
    #compute list of all assignees
    asses = set()
    for x in issues:
        asses.add(x.assignee)
    asses = list(asses)
    asses.sort(key = lambda x: x.lower())
#     print "ASSES:", asses
    
    #compute critical path
    x, crit = compute_crit(issues)
    
    #column for each assignee
    columns = []
    for ass in asses:
        col = [ass if ass else "_UNASSIGNED", []]
        for iss in issues:
            if iss.assignee == ass:
                card = {}
                card['num'] = iss.num
                card['title'] = iss.title           # + "|"+str(iss.auto_bb)
                card['body'] = iss.body
                card['comments'] = iss.comments
                card['link'] = '<a href="https://github.com/%s/%s/issues/%d" target="_blank">go to issue on github</a>' % (owner, repo, iss.num)
                card['labels'] = iss.labels
                card['length'] = iss.estimate
                card['start'], x = iss.crit_path()
                card['start'] -= iss.estimate
                card['BB'] = [x.num for x in iss.blocked_by if x.num not in iss.auto_bb]
                card['closed'] = False
                if iss.closed:
                    card['closed'] = True
                    card['color'] = '#9f9'
                elif 'READY' in iss.labels:
                    card['color'] = '#f0c0a7'
                elif 'INPROGRESS' in iss.labels:
                    card['color'] = '#fef2c0'
                elif 'TESTME' in iss.labels:
                    card['color'] = '#c7def8'
                else:
                    card['color'] = '#fab'
                if iss not in crit:
                    card['border'] = 'dashed'
                else:
                    card['bcolor'] = '#ff00ff'
                col[1].append(card)
        col[1].sort(key = lambda x: x['start'])
        columns.append(col)
    context['columns'] = columns
    context['day_width'] = DAYWIDTH
    context['card_width'] = CARDWIDTH
    context['tot_width_pad'] = DAYWIDTH + CARDWIDTH * len(context['columns'])
    context['tot_width'] = context['tot_width_pad'] -6

    return render(request, 'gittrack/templates/index.html', context)

def iss(request):
    context = dict(static_context)
    user = request.GET['user']
    pw = request.GET['pw']
    repo = request.GET['repo']
    iss = int(request.GET['issue'])
    context['repo'] = repo

    #very basic security
    print "PATH:", sys.path
    if config and user in config.user:
        if pw in config.user[user]['pw']:
            pw = config.user[user]['pw'][pw]
        else:
            return HttpResponse("bad password")
        user = config.user[user]['user']
        print "DEBUG using alias", user
    else:
        print "DEBUG not using alias, config=", config

    owner = request.GET['owner'] if 'owner' in request.GET else user
    context['owner'] = owner
       
    giss = get_issue(user, pw, repo, iss, owner)
    print "DEBUG get_issue returns:", repr(giss)
    if type(giss) in (str, unicode, type(None)):
        return HttpResponse(giss)
    else:
        return HttpResponse("issue#=%d %s |%s| milestone=%s assigned=%s labels=%s\n%s" % 
                            (iss, giss.state, giss.title, giss.milestone, giss.assignee, giss.labels, giss.body), content_type="text/plain")
