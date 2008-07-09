import os
import mimetypes

mimetypes.add_type('text/html', '.stx')
mimetypes.add_type('application/pdf', '.pdf')

from zope.component import getMultiAdapter
from zope.structuredtext import stx2html

from webob import Response

from repoze.bfg.interfaces import IViewFactory

class BrowserView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

class FileView(BrowserView):
    def __call__(self, *arg, **kw):
        dirname, filename = os.path.split(self.context.path)
        name, ext = os.path.splitext(filename)
        renderer = getMultiAdapter((self.context, self.request),
                                   IViewFactory, name=ext)
        result = renderer()
        return result

class DirectoryView(BrowserView):
    defaults = ('index.html', 'index.stx')
    def __call__(self, *arg, **kw):
        for name in self.defaults:
            try:
                index = self.context[name]
            except KeyError:
                continue
            fileview = FileView(index, self.request)
            return fileview()
        response = Response('No default view for %s' % self.context.path)
        response.content_type = 'text/plain'
        return response
        
class StructuredTextView(BrowserView):
    """ Filesystem-based STX view
    """
    def __call__(self, *arg, **kw):
        """ Render source as STX.
        """
        result = stx2html(self.context.source)
        response = Response(result)
        response.content_type = 'text/html'
        return response

class RawView(BrowserView):
    """ Just return the source raw.
    """
    def __call__(self, *arg, **kw):
        """ Render the result, guess content type.
        """
        response = Response(self.context.source)
        dirname, filename = os.path.split(self.context.path)
        name, ext = os.path.splitext(filename)
        mt, encoding = mimetypes.guess_type(filename)
        response.content_type = mt or 'text/plain'
        return response
