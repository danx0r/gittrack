#
# compute critical path and constrained subpaths given time and blocked-by data
#

class issue(object):
    num = 0                 #int
    assigned = ""           #string
    title = ""              #string
    body = ""               #string
    blocked_by = []         #list of ints / issues
    estimate = 0.0          #float, days

    def __init__(self, num=0, ass='', title="", body="", bb=[], est=0):
        self.num = num
        self.assigned = ass
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
    
    def __repr__(self):
        return "<issue %d %s>" % (self.num, self.title)

#parse BB and TE
def parse_issues(issues):
    map = {}
    for iss in issues:
        if iss == None:
            continue
        map[iss.num] = iss
    for iss in issues:
        if iss == None:
            continue
        s = iss.title + iss.body
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

if __name__ == '__main__':
    issues = [
        None,                    #ensure index = num
        issue(1, 'danx0r', "First task BB:4 TE:1"),
        issue(2, 'danx0r', "Second task BB:1 TE:1"),
        issue(4, 'danx0r', "Third task", "TE:3"),
    ]

    parse_issues(issues)    
    crit, path = compute_crit(issues)
    print "critical path days: %.2f issues: %s" % (crit, ["%d|%.2f" % (x.num, x.estimate) for x in path])
