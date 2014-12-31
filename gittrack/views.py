# from django.http import Http404
# from django.shortcuts import get_object_or_404, render
# from django.http import HttpResponse, HttpResponseRedirect
# from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, render_to_response

static_context = {
    'images': 'static/images/',
    'scripts': 'static/scripts/',
}

def home(request):
    context = dict(static_context)
    context['days'] = [
        {'dow': 'Friday', 'date': "2015/1/9", 'color': '#ddd',},
        {'dow': 'Monday', 'date': "2015/1/12", 'color': '#ddd'},
        {'dow': 'Tuesday', 'date': "2015/1/13", 'color': '#333', 'texcol':'white'},
    ]
    context['columns'] = [
        [
            'danx0r',
            [
                {'num':1, 'title': "Something's coming...", 'start': 0, 'length': .5, 'color': "#cce", 'border': 'dashed', 'bcolor': '#444'},
                {'num':2, 'BB': [1, 3], 'title': "Bad mojo bros!", 'start': 1.5, 'length': 1.5, 'color': "#cce", 'bcolor': '#ff00ff'}
            ]
        ],
        [
            'morashon',
            [
                {'num':3, 'title': "Return of the king bug", 'start': 0, 'length': 1.5, 'color': "#ecc", 'bcolor': '#ff00ff'}
            ]
        ]
    ]

    return render(request, 'gittrack/templates/index.html', context)
