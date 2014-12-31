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
    context['days'] = ["Friday<br/>2015/1/9","Monday<br/>2015/1/12"]
    context['columns'] = [
        [
            'danx0r',
            [
                {'num':2, 'BB': 3, 'title': "Bad mojo bros!", 'start': 1, 'length': 1}
            ]
        ],
        [
            'morashon',
            [
                {'num':3, 'title': "Return of the king bug", 'start': 0, 'length': 1.5}
            ]
        ]
    ]

    return render(request, 'gittrack/templates/index.html', context)
