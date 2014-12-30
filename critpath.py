#
# compute critical path and constrained subpaths given time and blocked-by data
#
import sys
import github3

def clean_cr(s):
    return s.replace('\r', '\n').rstrip()

class issue(object):
    num = 0                 #int
    assignee = ""           #string
    title = ""              #string
    body = ""               #string
    blocked_by = []         #list of ints / issues
    estimate = 0.0          #float, days
    labels = []             #list of strings
    mil_name = ''           #string
    mil_start = ''          #datetime or ''
    mil_due = ''            #datetime or ''

    def __init__(self, num=0, ass='', title="", body="", bb=[], est=0):
        self.num = num
        self.assignee = ass
        self.title = title
        self.body = body
        self.blocked_by = bb
        self.estimate = est

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
        return "<issue %d|%s|%s>" % (self.num, self.assignee, clean_cr(self.title))
    
    def bigrepr(self):
        return "<issue %d|%s|%s|%s est: %f mil: %s:%s:%s bb: %s labels: %s>" % (self.num, self.assignee, 
                        clean_cr(self.title), clean_cr(self.body).replace('\n', ' '), self.estimate,
                        clean_cr(self.mil_name), self.mil_start, self.mil_due, 
                        self.blocked_by, self.labels)

#find previous issue numerically for assignee
def map_prev_assignee(map, iss):
    i = iss.num - 1
    while i >= 0:
        if i in map and map[i].assignee == iss.assignee:
            return map[i]
        i -= 1

#parse BB and TE
#ensure no parallel work for one assignee
def parse_issues(issues):
    map = {}
    for iss in issues:
        if iss == None:
            continue
        map[iss.num] = iss

    for iss in issues:
        if iss == None:
            continue
        s = iss.title + iss.body if iss.body else ""
        i = s.rfind("TE:")
        if i >= 0:
            te = float(s[i+3:].split()[0])
            iss.estimate = te
        iss.blocked_by = []
        while "BB:" in s:
#             print s
            i = s.find("BB:") + 3
            s = s[i:]
            bb = int(s.split()[0])
            iss.blocked_by.append(map[bb])

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

    #DEBUG PRINTOUT
    for iss in issues:
        if iss == None:
            continue
        print "te %.2f bb for" % iss.estimate, iss, iss.blocked_by

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

def get_issues(user, pw, repo, owner=None):
#     global giss
    gh = github3.login(user, password=pw)
    if not owner:
        owner = user
    issues = []
    for giss in gh.iter_repo_issues(owner, repo):
        iss = issue(giss.number, str(giss.assignee), giss.title, giss.body)
        iss.labels = [str(x) for x in giss.labels]
        iss.mil_name = str(giss.milestone if giss.milestone else '')
        issues.append(iss)
    return issues

if __name__ == '__main__':
#     issues = [
#         None,                    #ensure index = num
#         issue(1, 'danx0r', "Fursst task TE:1.5 BB:2"),
#         issue(2, 'danx0r', "Secnd task TE:1"),
#         issue(4, 'silas', "Third task", "TE:2"),
#         issue(5, 'loren', "FORTH task", "TE:1 BB:2"),
#     ]
    issues = get_issues(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else sys.argv[1])
    for iss in issues:
        print "ISSUE:", iss.bigrepr()

    parse_issues(issues)    
    crit, path = compute_crit(issues)
    print "critical path days: %.2f path: %s" % (crit, ["%d|%.2f" % (x.num, x.estimate) for x in path])
