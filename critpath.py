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

    def __init__(self, num=0, title="", body="", bb=[], est=0):
        self.num = num
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

#replace indices with objects in blocked_by            
def fix_bb(issues):
    map = {}
    for iss in issues:
        if iss == None:
            continue
        map[iss.num] = iss
    for iss in issues:
        if iss == None:
            continue
        for j in range(len(iss.blocked_by)):
            bb = iss.blocked_by[j]
            if type(bb) == int:
                iss.blocked_by[j] = map[bb]

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
        issue(1, "First task", "", [4], 1),
        issue(2, "Second task", "", [1], 1),
        issue(4, "Third task", "", [], 3),
    ]

    fix_bb(issues)    
    crit, path = compute_crit(issues)
    print "critical path days: %f issues: %s" % (crit, ["%d|%f" % (x.num, x.estimate) for x in path])
