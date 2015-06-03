from __future__ import absolute_import

# import all test modules for the old test runner
from tests.unittests.test_index_creation import BackendTest as BT1  # noqa
from tests.unittests.test_query import BackendTest as BT2  # noqa
from tests.unittests.test_hooks import BackendTest as BT4  # noqa
from tests.functional_tests.test_query import BackendTest as BT3  # noqa
from tests.functional_tests.test_index_creation import IndexTest  # noqa
from tests.functional_tests.test_hooks import HookTest  # noqa
