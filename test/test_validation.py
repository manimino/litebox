from rangeindex import (
    RangeIndex,
    QueryMalformedError,
    QueryBadOperatorError,
    QueryBadNullComparator,
    QueryTypeError,
    QueryUnknownFieldError,
)
import unittest


class QueryValidationTests(unittest.TestCase):
    def test_ok_queries(self):
        ri = RangeIndex({"i": int, "s": str})
        ri.find([])
        ri.find([("i", "==", 3)])
        ri.find([("i", "==", 3), ("i", "is", None), ("s", "is not", None)])

    def test_bad_value_type(self):
        ri = RangeIndex({"i": int})
        with self.assertRaises(QueryTypeError):
            ri.find([("i", "==", "s")])

    def test_no_index_for_that(self):
        ri = RangeIndex({"i": int})
        with self.assertRaises(QueryUnknownFieldError):
            ri.find([("not_a_field", "==", "s")])

    def test_null_comparator(self):
        ri = RangeIndex({"i": int})
        with self.assertRaises(QueryBadNullComparator):
            ri.find([("i", ">", None)])

    def test_query_malformed(self):
        ri = RangeIndex({"i": int})
        with self.assertRaises(QueryMalformedError):
            ri.find([42])  # not an iterable
        with self.assertRaises(QueryMalformedError):
            ri.find([(1, 2)])  # not length 3

    def test_query_bad_operator(self):
        ri = RangeIndex({"i": int})
        with self.assertRaises(QueryBadOperatorError):
            ri.find([("i", "bad_operator", 42)])
