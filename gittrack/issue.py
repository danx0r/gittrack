#
# compute critical path and constrained subpaths given time and blocked-by data
#
import sys
import pytz, tzlocal
from dateutil.parser import parse as parse_dt
import github3
import jira

def clean_cr(s):
    if s == None:
        return ''
    return s.replace('\r', '\n').rstrip()

class issue(object):
#     num = 0                 #int
#     assignee = ""           #string
#     title = ""              #string
#     body = ""               #string
#     blocked_by = []         #list of ints / issues
#     auto_bb = []            #list of int id's of auto-blocked (don't display)
#     estimate = 0.5          #float, days
#     labels = []             #list of strings
#     mil_name = ''           #string
#     mil_start = ''          #datetime or ''
#     mil_due = ''            #datetime or ''

    def __init__(self, num=0, ass='', title="", body="", bb=[], est=0.5, name=""):
        self.num = num
        self.name = name
        self.assignee = ass
        self.title = title
        self.body = body
        self.estimate = est
        self.labels = []
        self.comments = []
        self.blocked_by = []
        self.auto_bb = []
        self.mil_name = ''
        self.mil_start = ''
        self.mil_due = ''
        self.closed = False

    def crit_path(self):
        days = 0
        path = []
        for bb in self.blocked_by:
            crit, nupth = bb.crit_path()
            if crit > days:
                days = crit
                path = nupth
        return self.estimate + days, path + [self]
    
    def is_bb(self, issue):
        return issue in self.blocked_by

    def __repr__(self):
#         return "<issue %d %s>" % (self.num, self.title)
        return "<#%d|%s|%s>" % (self.num, self.assignee, clean_cr(self.title))
    
    def bigrepr(self):
        return "<#%d|%s|%s|%s est: %.2f mil: %s|%s|%s bb: %s labels: %s>" % (self.num, self.assignee, 
                        clean_cr(self.title), clean_cr(self.body).replace('\n', ' '), self.estimate,
                        clean_cr(self.mil_name), 
                        self.mil_start.strftime("%Y-%m-%d_%H:%M") if self.mil_start else '', 
                        self.mil_due.strftime("%Y-%m-%d_%H:%M") if self.mil_due else '',
                        [x.num for x in self.blocked_by], 
                        self.labels)

#find previous issue numerically for assignee
def map_prev_assignee(map, iss):
    i = iss.num - 1
    while i >= 0:
        if i in map and map[i].assignee == iss.assignee:
            return map[i]
        i -= 1
    return None

#parse BB and TE
#ensure no parallel work for one assignee
def parse_issues(issues):
    print "ISSUES:", type(issues[0])
    map = {}
    for iss in issues:
        if iss == None:
            continue
        map[iss.num] = iss
    print"MAP:", map
    for iss in issues:
        if iss == None:
            continue
        #replace id nums w issue object
        for i in range(len(iss.blocked_by)):
            bb = iss.blocked_by[i]
            if bb in map:
                iss.blocked_by[i] = map[bb]
            else:
                print "ERR no bb", bb
        print "FIXED BB:", iss.blocked_by
#         s = iss.title + (" " + iss.body if iss.body else "")
#         for c in iss.comments:
#             s += " " + c
#         i = s.rfind("ESTIMATE DAYS:")
#         if i >= 0:
#             try:
#                 te = float(s[i+14:].split()[0])
#                 iss.estimate = te
#             except:
#                 print "unparsed ESTIMATE DAYS:"
#         iss.blocked_by = []
#         while "BLOCKED BY:" in s:
#             try:
#                 i = s.find("BLOCKED BY:") + 11
#                 s = s[i:]
#                 wrds = s.split()
#                 for b in wrds:
#                     bb = int(b.replace(',', ""))
#     #                 print "BB:", bb
#                     if bb in map:
#                         iss.blocked_by.append(map[bb])
#                     if ',' not in b:
#                         break
#             except:
#                 print "unparsed BLOCKED BY:"
    for iss in issues:
        #determine if any of our bb's are assigned to us
        flag = False
        for bb in iss.blocked_by:
            if bb.assignee == iss.assignee:
                flag = True
                break
        #if not, auto-bb previous issue if any
        if not flag:
            prev = map_prev_assignee(map, iss)
#             print "prev for", iss, "is:", prev
            if prev != None and not prev.is_bb(iss):
                iss.blocked_by.append(prev)
                iss.auto_bb.append(prev.num)

    #DEBUG PRINTOUT
#     for iss in issues:
#         if iss == None:
#             continue
#         print "te %.2f bb for" % iss.estimate, iss, iss.blocked_by

def compute_crit(issues):
    crit = 0
    path = []
    for i, iss in enumerate(issues):
        if iss == None:
            continue
        cp, pth = iss.crit_path()
        if cp > crit:
            crit = cp
            path = pth
    return crit, path

def get_ghrepo(gh, owner, repo):
    for r in gh.iter_repos():
        if str(r.owner) == owner and r.name == repo:
            return r

def get_milestone_id(repo, ms):
    for m in repo.iter_milestones():
        if str(m) == ms:
            return m.number

def get_issues(user, pw, repo, owner=None, mil=None):
    global gh, giss
    gh = github3.login(user, password=pw)
    if not owner:
        owner = user
    gr = get_ghrepo(gh, owner, repo)
    if not gr:
        return "ERROR: repo %s/%s not found (or %s lacks access)" % (owner, repo, user)
    if mil:
        tmil = mil
        mil = get_milestone_id(gr, mil)
        if not mil:
            return "ERROR: milestone %s not found" % tmil
    issues = []
    for giss in gh.iter_repo_issues(owner, repo, **({'state': 'all', 'milestone': mil} if mil else {'state': 'all'}) ):
        iss = issue(giss.number, str(giss.assignee) if giss.assignee else '', giss.title, giss.body)
        iss.labels = [str(x) for x in giss.labels]
        iss.comments = [x.body for x in giss.iter_comments()]
        if giss.milestone:
            iss.mil_name = str(giss.milestone)
            if giss.milestone.due_on:
                iss.mil_due = giss.milestone.due_on
            if "START:" in giss.milestone.description:
                i = giss.milestone.description.find("START:") + 6
                s = giss.milestone.description[i:].split()[0]
#                 print "PARSE DATE:", s
                iss.mil_start = tzlocal.get_localzone().localize(parse_dt(s)).astimezone(pytz.utc) #sheesh, is that really necessary?
        if giss.state == 'closed':
            iss.closed = True
        issues.append(iss)
#     issues.sort(key = lambda x: x.num)
    return issues

def get_issues_jira(user, pw, url, proj):
    aj = jira.JIRA(url, basic_auth=(user, pw))
    jisses = aj.search_issues("project=%s" % proj)
    issues = []
    for jiss in jisses:
        nom = str(jiss)
        nom = nom[nom.find('-')+1:]
        iss = issue(int(jiss.id), str(jiss.fields.assignee) if jiss.fields.assignee else '', jiss.fields.summary, jiss.fields.description, name=nom)
        for lnk in jiss.fields.issuelinks:
            if hasattr(lnk, 'inwardIssue'):
                iss.blocked_by.append(int(lnk.inwardIssue.id))
                print "BLOCKED by:", iss.blocked_by[-1]
        issues.append(iss)
        if jiss.fields.timeoriginalestimate:
            iss.estimate = jiss.fields.timeoriginalestimate / 28800.0
    return issues

def get_issue(user, pw, repo, iss, owner=None):
    global gh, giss
    gh = github3.login(user, password=pw)
    if not owner:
        owner = user
    gr = get_ghrepo(gh, owner, repo)
    if not gr:
        return "ERROR2: repo %s/%s not found (or %s lacks access)" % (owner, repo, user)
    giss = gh.issue(owner, repo, iss)
    print "DEBUG get_issue user=%s owner=%s repo=%s iss=%d giss=%s" % (user, owner, repo, iss, giss)
    return giss

def get_issue_jira(user, pw, url, iss):
    aj = jira.JIRA(url, basic_auth=(user, pw))
    jiss = aj.issue(iss)
    return jiss

if __name__ == '__main__':
    issues = [
        issue(1, 'danx0r', "Fursst task"),
        issue(2, 'danx0r', "Secnd task"),
        issue(3, 'danx0r', "FORTH task BLOCKED BY: 4"),
        issue(4, 'danx0r', "Third task"),
    ]
#     issues = get_issues(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else sys.argv[1], sys.argv[5] if len(sys.argv) > 5 else None)
    parse_issues(issues)
    for iss in issues:
        print "ISSUE:", iss.bigrepr()
    crit, path = compute_crit(issues)
    print "critical path days: %.2f path:" % crit
    for x in path:
        print " ", x.bigrepr(), x.auto_bb
