# -*- coding: utf-8 -*-
from collective.feedback.interfaces import ICollectiveFeedbackStore
from collective.feedback.testing import COLLECTIVE_FEEDBACK_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility

import transaction
import unittest


class TestTool(unittest.TestCase):
    layer = COLLECTIVE_FEEDBACK_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def tearDown(self):
        tool = getUtility(ICollectiveFeedbackStore)
        tool.clear()
        transaction.commit()

    def test_correctly_add_data(self):
        tool = getUtility(ICollectiveFeedbackStore)
        self.assertEqual(len(tool.search()), 0)
        tool.add({"vote": 4})
        self.assertEqual(len(tool.search()), 1)

    def test_only_store_defined_fields(self):
        tool = getUtility(ICollectiveFeedbackStore)
        self.assertEqual(len(tool.search()), 0)
        id = tool.add(
            {
                "vote": 4,
                "foo": "foo",
                "unknown": "mistery",
                "title": "title",
                "comment": "comment",
            }
        )
        self.assertEqual(len(tool.search()), 1)

        item = tool.get_record(id)
        self.assertEqual(item.attrs.get("unknown", None), None)
        self.assertEqual(item.attrs.get("foo", None), None)
        self.assertEqual(item.attrs.get("vote", None), 4)
        self.assertEqual(item.attrs.get("title", None), "title")
        self.assertEqual(item.attrs.get("comment", None), "comment")

    def test_update_record(self):
        tool = getUtility(ICollectiveFeedbackStore)
        id = tool.add({"vote": 4, "comment": "is ok"})

        item = tool.get_record(id)
        self.assertEqual(item.attrs.get("vote", None), 4)
        self.assertEqual(item.attrs.get("comment", None), "is ok")

        tool.update(id=id, data={"vote": 2, "comment": "not ok"})
        item = tool.get_record(id)
        self.assertEqual(item.attrs.get("vote", None), 2)
        self.assertEqual(item.attrs.get("comment", None), "not ok")

    def test_update_record_return_error_if_id_not_found(self):
        tool = getUtility(ICollectiveFeedbackStore)
        res = tool.update(id=1222, data={})
        self.assertEqual(res, {"error": "NotFound"})

    def test_delete_record(self):
        tool = getUtility(ICollectiveFeedbackStore)
        foo = tool.add({"vote": 1, "comment": "is ok", "uid": 1234})
        tool.add({"vote": 1, "comment": "is ok", "uid": 5678})

        self.assertEqual(len(tool.search()), 2)
        tool.delete(id=foo)
        self.assertEqual(len(tool.search()), 1)

    def test_delete_record_return_error_if_id_not_found(self):
        tool = getUtility(ICollectiveFeedbackStore)
        res = tool.delete(id=1222)
        self.assertEqual(res, {"error": "NotFound"})

    def test_clear(self):
        tool = getUtility(ICollectiveFeedbackStore)
        tool.add({"vote": 1, "comment": "is ok", "uid": 1234})
        tool.add({"vote": 1, "comment": "is ok", "uid": 5678})
        transaction.commit()

        self.assertEqual(len(tool.search()), 2)

        tool.clear()
        self.assertEqual(len(tool.search()), 0)
