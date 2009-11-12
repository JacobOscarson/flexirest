# -*- coding: utf-8 -*-
from __future__ import with_statement

import os
import sys
from StringIO import StringIO

MINIMAL_FIXTURE = """
=================
A minimal fixture
=================
Text
"""

UTF8_FIXTURE = """
=====
Titel
=====

Svensk text här.
"""

get_minimal_fixture = lambda: StringIO(MINIMAL_FIXTURE)
get_utf8_fixture = lambda: StringIO(UTF8_FIXTURE)

def getraise(callable, *args, **kwargs):
    """
    Calls `callable`, expecting an exception inheriting from
    StandardError (your exceptions *are* inheriting from
    StandardError, right?), with `*args` and `**kwargs` as parameters.

    Returns the results of `sys.exc_info()` as a result.

    Isn't there something built into nose that does this? I can't find
    it.

    >>> _type, exc, tb = getraise(open, '/no/such/path')
    >>> exc
    IOError(2, 'No such file or directory')
    >>>
    """
    try:
        callable(*args, **kwargs)
    except StandardError:
        return sys.exc_info()

class Capturer(object):
    """
    User by test_main to capture output from main.commandline(). The
    capturer is any object that supports a .write() method (`sys.stdout`
    would be used in production code).
    """
    def __init__(self):
        self.lines = []

    def write(self, msg):
        self.lines.append(msg)

    def flush(self):
        pass

testfiles = []

def write_test_file(path, contents):
    with open(path, 'w') as fp:
        fp.write(contents)

def create_gc_testfile(path, contents):
    write_test_file(path, contents)
    testfiles.append(path)

def clean_gc_testfiles():
    for path in testfiles:
        os.unlink(path)
        testfiles.remove(path)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
