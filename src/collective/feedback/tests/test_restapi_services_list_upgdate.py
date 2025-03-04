# -*- coding: utf-8 -*-
from collective.feedback.interfaces import ICollectiveFeedbackStore
from collective.feedback.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

import transaction
import unittest


class TestAdd(unittest.TestCase):
    layer = RESTAPI_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.portal_url_path = self.portal.absolute_url_path()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.user.create(
            email="memberuser@example.com",
            username="memberuser",
            password="secret!!",
        )

        self.document = api.content.create(
            title="Document", container=self.portal, type="Document"
        )
        api.content.transition(obj=self.document, transition="publish")

        self.private_document = api.content.create(
            title="restricted document", container=self.portal, type="Document"
        )
        transaction.commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        self.url = "{}/@feedback-add".format(self.portal_url)
        self.document_path = self.document.absolute_url_path().replace(
            self.portal.absolute_url_path(), ""
        )
        self.private_document_path = self.private_document.absolute_url_path().replace(
            self.portal.absolute_url_path(), ""
        )

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_correctly_update_data(self):
        self.anon_api_session.post(
            self.url,
            json={
                "vote": 3,
                "comment": "i disagree",
                "honey": "",
                "content": self.document_path,
            },
        )
        self.anon_api_session.post(
            self.url,
            json={
                "vote": 2,
                "comment": "i disagree",
                "honey": "",
                "content": self.document_path,
            },
        )
        transaction.commit()
        tool = getUtility(ICollectiveFeedbackStore)
        feedbacks = tool.search()

        self.assertEqual(len(feedbacks), 2)

        self.api_session.patch(
            self.portal_url + "/@feedback-list",
            json={str(feedbacks[0].intid): {"read": True}},
        )
        transaction.commit()

        self.assertTrue(tool.get(feedbacks[0].intid).attrs.get("read"))

    def test_unknown_id(self):
        self.anon_api_session.post(
            self.url,
            json={
                "vote": 3,
                "comment": "i disagree",
                "honey": "",
                "content": self.document_path,
            },
        )
        transaction.commit()

        tool = getUtility(ICollectiveFeedbackStore)
        feedbacks = tool.search()

        self.assertEqual(len(feedbacks), 1)

        resp = self.api_session.patch(
            self.portal_url + "/@feedback-list",
            json={"1111111111": {"read": True}},
        )

        transaction.commit()

        self.assertEqual(resp.status_code, 404)

    def test_bad_id(self):
        self.anon_api_session.post(
            self.url,
            json={
                "vote": 3,
                "comment": "i disagree",
                "honey": "",
                "content": self.document_path,
            },
        )
        transaction.commit()

        tool = getUtility(ICollectiveFeedbackStore)
        feedbacks = tool.search()

        self.assertEqual(len(feedbacks), 1)

        resp = self.api_session.patch(
            self.portal_url + "/@feedback-list",
            json={"fffffffff": {"read": True}},
        )

        transaction.commit()

        self.assertEqual(resp.status_code, 400)
