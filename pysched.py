from pyschedule import Scenario, solvers, plotters

def run(S) :
    if solvers.mip.solve(S):
#         %matplotlib inline
        plotters.matplotlib.plot(S,task_colors=task_colors,fig_size=(10,5))
    else:
        print('no solution exists')

S = Scenario('bike_paint_shop', horizon=10)

Alice = S.Resource('Alice')
Bob = S.Resource('Bob')

green_paint, red_paint = S.Task('green_paint', length=2), S.Task('red_paint', length=2)
green_post, red_post = S.Task('green_post'), S.Task('red_post')

S += green_paint < green_post, red_paint + 1 <= red_post

# green_paint += Alice|Bob
# green_post += Alice|Bob
# 
# red_paint += Alice|Bob
# red_post += Alice|Bob

S.clear_solution()
S.use_makespan_objective()

task_colors = { green_paint   : '#A1D372',
                green_post    : '#A1D372', 
                red_paint     : '#EB4845',
                red_post      : '#EB4845',
                S['MakeSpan'] : '#7EA7D8'}

# First remove the old resource to task assignments
# green_paint -= Alice|Bob
# green_post -= Alice|Bob
# red_paint -= Alice|Bob
# red_post -= Alice|Bob

# Add new shared ones
green_resource = Alice|Bob
green_paint += green_resource
green_post += green_resource

red_resource = Alice|Bob
red_paint += red_resource
red_post += red_resource

Paint_Shop = S.Resource('Paint_Shop')
red_paint += Paint_Shop
green_paint += Paint_Shop

Lunch = S.Task('Lunch')
Lunch += {Alice, Bob}
S += Lunch > 3, Lunch < 5
task_colors[Lunch] = '#7EA7D8'
S += red_paint > 2

#Alice is a morning bird
S += Alice['length'][:3] >= 3

print(S)
run(S)
