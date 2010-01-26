from __future__ import with_statement

import mock

from nose.tools import assert_equals, assert_true, with_setup

from aspektratio.util import substitute

from flexirest.strategies import check_writers

da_func = mock.Mock()
da_func.isfunctional.return_value = True
da_not_func = mock.Mock()
da_not_func.isfunctional.return_value = False

def test_check_writers_both():
    """
    Tests that `check_writers` returns both functional and
    non-functional writers.
    """
    funcs, notfuncs = check_writers({
        'first_func': da_func,
        'second_nofunc': da_not_func,
        'third_func': da_func
    })

    assert_equals(set(funcs.keys()), set(('first_func', 'third_func')) )
    assert_equals(set(notfuncs.keys()), set(('second_nofunc',)) )

def test_check_writers_integration_sanity():
    """
    Sanity check: certain writers should always be functional.
    """
    funcs, notfuncs = check_writers()
    # The following writers should always work, otherwise it's an indication
    # that something is wrong.
    must_work = set(('html', 'latex', 'xml', 's5', 'pseudoxml', 'rtf'))
    assert_equals(must_work - set(funcs.keys()), set())
