import logging
import traceback

from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from djblets.siteconfig.models import SiteConfiguration
from djblets.util.misc import cache_memoize, get_object_or_none

from reviewboard.diffviewer.models import DiffSet, FileDiff
from reviewboard.diffviewer.diffutils import UserVisibleError, \
                                             get_diff_files, \
                                             get_enable_highlighting
from reviewboard.scmtools.core import SCMError


def build_diff_fragment(request, file, chunkindex, highlighting, collapseall,
                        context,
                        template_name='diffviewer/diff_file_fragment.html'):
    key = template_name + '-'

    if file['force_interdiff']:
        if file['interfilediff']:
            key += 'interdiff-%s-%s' % (file['filediff'].id,
                                        file['interfilediff'].id)
        else:
            key += 'interdiff-%s-none' % file['filediff'].id
    else:
        key += str(file['filediff'].id)

    if chunkindex:
        chunkindex = int(chunkindex)
        if chunkindex < 0 or chunkindex >= len(file['chunks']):
            raise UserVisibleError(_(u"Invalid chunk index %s specified.") % \
                                   chunkindex)

        file['chunks'] = [file['chunks'][chunkindex]]
        key += '-chunk-%s' % chunkindex

    if collapseall:
        key += '-collapsed'
        context['collapseall'] = True

    if highlighting:
        key += '-highlighting'

    key += '-' + settings.AJAX_SERIAL

    context['file'] = file

    return cache_memoize(key,
        lambda: render_to_string(template_name,
                                 RequestContext(request, context)))


def get_collapse_diff(request):
    if request.GET.get('expand', False):
        return False
    elif request.GET.get('collapse', False):
        return True
    elif request.COOKIES.has_key('collapsediffs'):
        return (request.COOKIES['collapsediffs'] == "True")
    else:
        return True


def view_diff(request, diffset_id, interdiffset_id=None, extra_context={},
              template_name='diffviewer/view_diff.html'):
    diffset = get_object_or_404(DiffSet, pk=diffset_id)
    interdiffset = get_object_or_none(DiffSet, pk=interdiffset_id)
    highlighting = get_enable_highlighting(request.user)

    try:
        if interdiffset_id:
            logging.debug("Generating diff viewer page for interdiffset ids "
                          "%s-%s",
                          diffset_id, interdiffset_id)
        else:
            logging.debug("Generating diff viewer page for filediff id %s",
                          diffset_id)

        files = get_diff_files(diffset, None, interdiffset,
                               highlighting, False)

        # Break the list of files into pages
        siteconfig = SiteConfiguration.objects.get_current()

        paginator = Paginator(files,
                              siteconfig.get("diffviewer_paginate_by"),
                              siteconfig.get("diffviewer_paginate_orphans"))

        page_num = int(request.GET.get('page', 1))

        if request.GET.get('file', False):
            file_id = int(request.GET['file'])

            for i, f in enumerate(files):
                if f['filediff'].id == file_id:
                    page_num = i // paginator.per_page + 1
                    if page_num > paginator.num_pages:
                        page_num = paginator.num_pages
                    break

        page = paginator.page(page_num)

        context = {
            'diffset': diffset,
            'interdiffset': interdiffset,
            'diffset_pair': (diffset, interdiffset),
        }
        context.update(extra_context)

        context['files'] = page.object_list

        # Add the pagination context
        context['is_paginated'] = page.has_other_pages()
        context['page'] = page.number
        context['pages'] = paginator.num_pages
        context['page_numbers'] = paginator.page_range
        context['has_next'] = page.has_next()
        context['next_page'] = page.next_page_number()
        context['has_previous'] = page.has_previous()
        context['previous_page'] = page.previous_page_number()
        context['page_start_index'] = page.start_index()

        response = render_to_response(template_name,
                                      RequestContext(request, context))
        response.set_cookie('collapsediffs', get_collapse_diff(request))

        if interdiffset_id:
            logging.debug("Done generating diff viewer page for interdiffset "
                          "ids %s-%s",
                          diffset_id, interdiffset_id)
        else:
            logging.debug("Done generating diff viewer page for filediff "
                          "id %s",
                          diffset_id)

        return response

    except Exception, e:
        return exception_traceback(request, e, template_name)


def view_diff_fragment(
        request, diffset_id, filediff_id, interdiffset_id=None,
        chunkindex=None,
        template_name='diffviewer/diff_file_fragment.html',
        error_template_name='diffviewer/diff_fragment_error.html'):

    def get_requested_diff_file(get_chunks=True):
        files = get_diff_files(diffset, filediff, interdiffset, highlighting,
                               get_chunks)

        if files:
            assert len(files) == 1
            file = files[0]

            if 'index' in request.GET:
                file['index'] = request.GET.get('index')

            return file

        return None

    diffset = get_object_or_404(DiffSet, pk=diffset_id)
    filediff = get_object_or_404(FileDiff, pk=filediff_id, diffset=diffset)
    interdiffset = get_object_or_none(DiffSet, pk=interdiffset_id)
    highlighting = get_enable_highlighting(request.user)

    if chunkindex:
        collapseall = False
    else:
        collapseall = get_collapse_diff(request)

    try:
        file = get_requested_diff_file()

        if file:
            context = {
                'standalone': chunkindex is not None,
            }

            return HttpResponse(build_diff_fragment(request, file,
                                                    chunkindex,
                                                    highlighting, collapseall,
                                                    context, template_name))
        raise UserVisibleError(
            _(u"Internal error. Unable to locate file record for filediff %s") % \
            filediff.id)
    except Exception, e:
        extra_context = {}

        file = get_requested_diff_file(False)
        extra_context['file'] = file

        return exception_traceback(request, e, error_template_name,
                                   extra_context)


def exception_traceback(request, e, template_name, extra_context={}):
    context = { 'error': e }
    context.update(extra_context)
    if e.__class__ is not UserVisibleError:
        context['trace'] = traceback.format_exc()

    return HttpResponseServerError(
        render_to_string(template_name, RequestContext(request, context)))
