"""Test running script for the `sublemon` library."""

import os
import sys

from doctest import (
    DocFileSuite,
    IGNORE_EXCEPTION_DETAIL)
from unittest import (
    defaultTestLoader,
    TextTestRunner)

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(HERE, 'docs')
TEST_DIR = os.path.join(HERE, 'tests')


def test():
    """Collect all unit and doct tests and run the test suite."""
    suite = defaultTestLoader.discover(
        TEST_DIR,
        'test_*.py',
        top_level_dir=HERE)

    doctest_kwargs = dict(optionflags=IGNORE_EXCEPTION_DETAIL)
    doctest_files = [
        os.path.join(DOCS_DIR, 'exceptions.md'),
        os.path.join(DOCS_DIR, 'index.md'),
        os.path.join(DOCS_DIR, 'sublemon-objects.md'),
        os.path.join(DOCS_DIR, 'subprocess-objects.md'),
        os.path.join(DOCS_DIR, 'utilities.md'),
    ]

    for f in doctest_files:
        doc_tests = DocFileSuite(f, module_relative=False, **doctest_kwargs)
        suite.addTests(doc_tests)

    runner = TextTestRunner()
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    sys.exit(0 if test() else 1)
