from rangeindex.rangeindex import (
    RangeIndex,
    QueryMalformedError,
    QueryBadOperatorError,
    QueryTypeError,
    QueryUnknownFieldError
)
import unittest


class QueryValidationTests(unittest.TestCase):

    def test_ok_queries(self):
        ri = RangeIndex({'i': int, 's': str})
        ri.find([])
        ri.find([('i', '==', 3)])
        ri.find([('i', '==', 3), ('i', '==', None), ('s', '!=', None)])

    def test_bad_value_type(self):
        ri = RangeIndex({'i': int})
        with self.assertRaises(QueryTypeError):
            ri.find([('i', '==', 's')])

    def test_no_index_for_that(self):
        ri = RangeIndex({'i': str})
        with self.assertRaises(QueryUnknownFieldError):
            ri.find([('not_a_field', '==', 's')])
