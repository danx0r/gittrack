# from django.http import Http404
# from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse#, HttpResponseRedirect
# from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, render_to_response
import datetime
from issue import *

static_context = {
    'images': 'static/images/',
    'scripts': 'static/scripts/',
}

def home(request):
    context = dict(static_context)
#     context['days'] = [
#         {'dow': 'Friday', 'date': "2015/1/9", 'color': '#ddd',},
#         {'dow': 'Monday', 'date': "2015/1/12", 'color': '#ddd'},
#         {'dow': 'Tuesday', 'date': "2015/1/13", 'color': '#333', 'texcol':'white'},
#     ]
#     context['columns'] = [
#         [
#             'danx0r',
#             [
#                 {'num':1, 'title': "Something's coming...", 'start': 0, 'length': .5, 'color': "#cce", 'border': 'dashed', 'bcolor': '#444'},
#                 {'num':2, 'BB': [1, 3], 'title': "Bad mojo bros!", 'start': 1.5, 'length': 1.5, 'color': "#cce", 'bcolor': '#ff00ff'}
#             ]
#         ],
#         [
#             'morashon',
#             [
#                 {'num':3, 'title': "Return of the king bug", 'start': 0, 'length': 1.5, 'color': "#ecc", 'bcolor': '#ff00ff'}
#             ]
#         ]
#     ]
    user = request.GET['user']
    repo = request.GET['repo']
    mil = request.GET['milestone']
    owner = request.GET['owner'] if 'owner' in request.GET else user
    pw = request.GET['pw']
    print ("REPO:", repo, "OWNER:", owner, "USER:", user, "MILESTONE:", mil)
    issues = get_issues(user, pw, repo, owner, mil)
    parse_issues(issues)    
    for iss in issues:
        print "ISSUE:", iss.bigrepr()
    crit, path = compute_crit(issues)
    print "critical path days: %.2f path: %s" % (crit, ["%d|%.2f" % (x.num, x.estimate) for x in path])

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
    print "start date:", start, "due date:", due
    days = []
    today = start
    while today <= due:
        day = {}
        day['date'] = today.strftime("%Y-%m-%d")
        day['dow'] = today.strftime("%A")
        day['color'] = "#ddd"
        days.append(day)
        today += datetime.timedelta(days = 1)
        #everybody's working 4 the wkend
        if today.strftime("%A") == 'Saturday':
            today += datetime.timedelta(days = 2)            
    print "DAYS:", days
    context['days'] = days
    
    #compute list of all assignees
    asses = set()
    for x in issues:
        asses.add(x.assignee)
    print "ASSES:", asses
    
    #compute critical path
    x, crit = compute_crit(issues)
    
    #column for each assignee
    columns = []
    for ass in asses:
        col = [ass if ass else "UNASSIGNED", []]
        for iss in issues:
            if iss.assignee == ass:
                card = {}
                card['num'] = iss.num
                card['title'] = iss.title           # + "|"+str(iss.auto_bb)
                card['length'] = iss.estimate
                card['start'], x = iss.crit_path()
                card['start'] -= iss.estimate
                card['BB'] = [x.num for x in iss.blocked_by if x.num not in iss.auto_bb]
                if 'READY' in iss.labels:
                    card['color'] = '#fac8a7'
                if 'INPROGRESS' in iss.labels:
                    card['color'] = '#fef2c0'
                if 'TESTME' in iss.labels:
                    card['color'] = '#c7def8'
                if iss not in crit:
                    card['border'] = 'dashed'
                else:
                    card['bcolor'] = '#ff00ff'
                col[1].append(card)
        columns.append(col)
    context['columns'] = columns

    return render(request, 'gittrack/templates/index.html', context)
