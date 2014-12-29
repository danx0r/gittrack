#
# compute critical path and constrained subpaths given time and blocked-by data
#

class issue(object):
    num = 0                 #int
    assignee = ""           #string
    title = ""              #string
    body = ""               #string
    blocked_by = []         #list of ints / issues
    estimate = 0.0          #float, days

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
    
    def __repr__(self):
        return "<issue %d %s>" % (self.num, self.title)

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
            if prev != None:
                iss.blocked_by.append(prev)
            
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
        issue(1, 'danx0r', "First task TE:1"),
        issue(2, 'danx0r', "Second task TE:1.5"),
        issue(4, 'silas', "Third task", "TE:2 BB:1"),
    ]

    parse_issues(issues)    
    crit, path = compute_crit(issues)
    print "critical path days: %.2f path: %s" % (crit, ["%d|%.2f" % (x.num, x.estimate) for x in path])
