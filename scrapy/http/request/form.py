"""
This module implements the FormRequest class which is a more convenient class
(than Request) to generate Requests based on form data.

See documentation in docs/topics/request-response.rst
"""

import six
from six.moves.urllib.parse import urljoin, urlencode

import lxml.html
from parsel.selector import create_root_node
from w3lib.html import strip_html5_whitespace

from scrapy.http.request import Request
from scrapy.utils.python import to_bytes, is_listlike
from scrapy.utils.response import get_base_url


class FormRequest(Request):

    def __init__(self, *args, **kwargs):
        formdata = kwargs.pop('formdata', None)
        if formdata and kwargs.get('method') is None:
            kwargs['method'] = 'POST'

        super(FormRequest, self).__init__(*args, **kwargs)

        if formdata:
            items = formdata.items() if isinstance(formdata, dict) else formdata
            querystr = _urlencode(items, self.encoding)
            if self.method == 'POST':
                self.headers.setdefault(b'Content-Type', b'application/x-www-form-urlencoded')
                self._set_body(querystr)
            else:
                self._set_url(self.url + ('&' if '?' in self.url else '?') + querystr)

    @classmethod
    def from_response(cls, response, formname=None, formid=None, formnumber=0, formdata=None,
                      clickdata=None, dont_click=False, formxpath=None, formcss=None, **kwargs):

        kwargs.setdefault('encoding', response.encoding)

        if formcss is not None:
            from parsel.csstranslator import HTMLTranslator
            formxpath = HTMLTranslator().css_to_xpath(formcss)

        form = _get_form(response, formname, formid, formnumber, formxpath)
        formdata = _get_inputs(form, formdata, dont_click, clickdata, response)
        url = _get_form_url(form, kwargs.pop('url', None))
        method = kwargs.pop('method', form.method)
        return cls(url=url, method=method, formdata=formdata, **kwargs)


def _get_form_url(form, url):
    if url is None:
        action = form.get('action')
        if action is None:
            return form.base_url
        return urljoin(form.base_url, strip_html5_whitespace(action))
    return urljoin(form.base_url, url)


def _urlencode(seq, enc):
    values = [(to_bytes(k, enc), to_bytes(v, enc))
              for k, vs in seq
              for v in (vs if is_listlike(vs) else [vs])]
    return urlencode(values, doseq=1)


def _get_form(response, formname, formid, formnumber, formxpath):
    """ Only tested from the form_request method, an be found above """
    """
    Requirements
    If no Form tag exists in the given response body, the program should error out.
    If there exists a formname that matches the input formname then that form shall be returned.
    If the formname does not exist the program shall continue.
    If there exists a formID that matches the input formname then that form shall be returned.
    If the formID does not exist the program shall continue.
    User-defined XML can be applyed to find a form and returned to the user.
    PARTLY UNTESTED - If user XML is faulty and no forms are found, throw an error.
    The user can specify which form in the list of found forms to be returned.
    If the formnumber is not specified and no forms found, return None.
    If the form number does not corespod to an indes of found forms, throw error.
    """
    """Find the form element """
    covFile = open("/home/koski/Desktop/scrapy/coverage/http_request_form__get_form.txt", "a")

    root = create_root_node(response.text, lxml.html.HTMLParser,
                            base_url=get_base_url(response))
    forms = root.xpath('//form')
    if not forms:
        covFile.write("0001\n")
        raise ValueError("No <form> element found in %s" % response)
    else:
        covFile.write("0019\n")

    if formname is not None:
        covFile.write("0002\n")
        f = root.xpath('//form[@name="%s"]' % formname)
        if f:
            covFile.write("0003\n")
            return f[0]
        covFile.write("0004\n")
    else:
        covFile.write("0020\n")

    if formid is not None:
        covFile.write("0005\n")
        f = root.xpath('//form[@id="%s"]' % formid)
        if f:
            covFile.write("0006\n")
            return f[0]
    else:
        covFile.write("0021\n")

    # Get form element from xpath, if not found, go up
    if formxpath is not None:
        covFile.write("0007\n")
        nodes = root.xpath(formxpath)
        if nodes:
            covFile.write("0008\n")
            el = nodes[0]
            while True:
                if el.tag == 'form':
                    covFile.write("0009\n")
                    return el
                el = el.getparent()
                if el is None:
                    covFile.write("0010\n") ## THIS IS NEVER REACHED
                    break
                covFile.write("0011\n")
            covFile.write("0012\n")  ## THIS IS NEVER REACHED BECAUSE OF NO. 10
        else:
            covFile.write("0022\n")
        covFile.write("0013\n")
        encoded = formxpath if six.PY3 else formxpath.encode('unicode_escape')
        raise ValueError('No <form> element found with %s' % encoded)
    else:
        covFile.write("0013\n")

    covFile.write("0014\n")
    # If we get here, it means that either formname was None
    # or invalid
    if formnumber is not None:
        covFile.write("0015\n")
        try:
            form = forms[formnumber]
        except IndexError:
            covFile.write("0016\n")
            raise IndexError("Form number %d not found in %s" %
                             (formnumber, response))
        else:
            covFile.write("0017\n")
            return form
    else:
        covFile.write("0018\n")


def _get_inputs(form, formdata, dont_click, clickdata, response):
    """
    Requirements

    """
    covFile = open("/home/koski/Desktop/scrapy/coverage/http_request_form__get_inputs.txt", "a")

    try:
        formdata = dict(formdata or ())
        covFile.write("0001\n")
    except (ValueError, TypeError):
        covFile.write("0002\n") ## THIS IS NEVER REACHED
        raise ValueError('formdata should be a dict or iterable of tuples')

    inputs = form.xpath('descendant::textarea'
                        '|descendant::select'
                        '|descendant::input[not(@type) or @type['
                        ' not(re:test(., "^(?:submit|image|reset)$", "i"))'
                        ' and (../@checked or'
                        '  not(re:test(., "^(?:checkbox|radio)$", "i")))]]',
                        namespaces={
                            "re": "http://exslt.org/regular-expressions"})
    values = [(k, u'' if v is None else v)
              for k, v in (_value(e) for e in inputs)
              if k and k not in formdata]

    if not dont_click:
        covFile.write("0003\n")
        clickable = _get_clickable(clickdata, form)
        if clickable and clickable[0] not in formdata and not clickable[0] is None:
            covFile.write("0004\n")
            values.append(clickable)
        else:
            covFile.write("0006\n")
    else:
        covFile.write("0007\n")

    covFile.write("0005\n")
    values.extend((k, v) for k, v in formdata.items() if v is not None)
    return values


def _value(ele):
    n = ele.name
    v = ele.value
    if ele.tag == 'select':
        return _select_value(ele, n, v)
    return n, v


def _select_value(ele, n, v):
    multiple = ele.multiple
    if v is None and not multiple:
        # Match browser behaviour on simple select tag without options selected
        # And for select tags wihout options
        o = ele.value_options
        return (n, o[0]) if o else (None, None)
    elif v is not None and multiple:
        # This is a workround to bug in lxml fixed 2.3.1
        # fix https://github.com/lxml/lxml/commit/57f49eed82068a20da3db8f1b18ae00c1bab8b12#L1L1139
        selected_options = ele.xpath('.//option[@selected]')
        v = [(o.get('value') or o.text or u'').strip() for o in selected_options]
    return n, v


def _get_clickable(clickdata, form):
    covFile = open("/home/koski/Desktop/scrapy/coverage/http_request_form__get_clickable.txt", "a")

    """
    Returns the clickable element specified in clickdata,
    if the latter is given. If not, it returns the first
    clickable element found

    Requirements:
    If a clickable element (a submit btn or a regular btn) does not exist the function should return None.
    If no data on which clickable event the user wants, the first found clickable event shall be returned.
    If a number is specified, the clickable with that ID shall be returned-
    Otherwise if the number of clickable elements is one, then that clickable shall be returned.
    If there are ambiguity in which one to shoose, the prgram should error out.
    If there are no elements the program should error out.
    """
    clickables = [
        el for el in form.xpath(
            'descendant::*[(self::input or self::button)'
            ' and re:test(@type, "^submit$", "i")]'
            '|descendant::button[not(@type)]',
            namespaces={"re": "http://exslt.org/regular-expressions"})
        ]
    if not clickables:
        covFile.write("0001\n")
        return

    # If we don't have clickdata, we just use the first clickable element
    if clickdata is None:
        covFile.write("0002\n")
        el = clickables[0]
        return (el.get('name'), el.get('value') or '')

    # If clickdata is given, we compare it to the clickable elements to find a
    # match. We first look to see if the number is specified in clickdata,
    # because that uniquely identifies the element
    nr = clickdata.get('nr', None)
    if nr is not None:
        covFile.write("0003\n")
        try:
            el = list(form.inputs)[nr]
        except IndexError:
            covFile.write("0004\n")
            pass
        else:
            covFile.write("0005\n")
            return (el.get('name'), el.get('value') or '')
    else:
        covFile.write("0009\n")
    # We didn't find it, so now we build an XPath expression out of the other
    # arguments, because they can be used as such
    xpath = u'.//*' + \
            u''.join(u'[@%s="%s"]' % c for c in six.iteritems(clickdata))
    el = form.xpath(xpath)
    if len(el) == 1:
        covFile.write("0006\n")
        return (el[0].get('name'), el[0].get('value') or '')
    elif len(el) > 1:
        covFile.write("0007\n")
        raise ValueError("Multiple elements found (%r) matching the criteria "
                         "in clickdata: %r" % (el, clickdata))
    else:
        covFile.write("0008\n")
        raise ValueError('No clickable element matching clickdata: %r' % (clickdata,))
