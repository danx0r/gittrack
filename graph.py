'''
Code problem: testing acyclicity

Given a directed graph with n vertices and m edges (1<=n,m<=103). Output 1 if the graph contains a cycle and 0 otherwise.


Sample Input:
4 4
1 2
4 1
2 3
3 1
'''


# initialize
line = raw_input()
array = [int(i) for i in line.split()]
n = array[0]
m = array[1]
graph = {}
index = 1
pre = [0] * (n + 1)
post = [0] * (n + 1)

for i in range(m):
    line = raw_input()
    array = [int(i) for i in line.split()]
    u = array[0]
    v = array[1]
    if u not in graph:
        graph[u] = [v]
    else:
        if v not in graph[u]:
            graph[u] += [v]

#print(graph)



def DFS(i):
    for j in graph[i]:
        #print("j = ", j)
        if vertices[j] == 1:
            global flag
            flag = 1
            #print("assigned flag to 1, j == ", j)
            break
        else:
            if j in graph:
                vertices[j] = 1
                DFS(j)
        vertices[j] = 0

flag = 0
vertices = [0] * (n + 1)
for i in graph:
    print("i = ", i)
    vertices[i] = 1
    if i in graph:
        print("i = ", i, " and DFS called ")
        DFS(i)
    if flag == 1:
        break
    vertices[i] = 0

# print(flag)
print "CYCLIC" if flag else "ACYCLIC"
