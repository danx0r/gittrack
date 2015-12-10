#
# get comments
#
import sys
import pytz, tzlocal
import github3
from issue import get_ghrepo

def get_comments(user, pw, repo, issue, owner=None):
    global gh
    gh = github3.login(user, password=pw)
    if not owner:
        owner = user
    gr = get_ghrepo(gh, owner, repo)
    if not gr:
        return "ERROR: repo %s/%s not found (or %s lacks access)" % (owner, repo, user)
    comments = []
    iss = gh.issue(owner, repo, issue)
    print iss
    for com in iss.iter_comments():
        print com
#     return issues

if __name__ == '__main__':
    get_comments("danx0r", sys.argv[1], "testrepo", 2)