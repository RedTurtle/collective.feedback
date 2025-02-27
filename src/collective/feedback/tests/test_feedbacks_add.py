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
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.user.create(
            email="memberuser@example.com",
            username="memberuser",
            password="secret!!",
        )

        self.document = api.content.create(
            title="Document", container=self.portal, type="Document"
        )
        self.document_path = self.document.absolute_url_path().replace(
            self.portal.absolute_url_path(), ""
        )
        api.content.transition(obj=self.document, transition="publish")

        self.private_document = api.content.create(
            title="restricted document", container=self.portal, type="Document"
        )
        self.private_document_path = self.private_document.absolute_url_path().replace(
            self.portal.absolute_url_path(), ""
        )
        transaction.commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        self.url = "{}/@feedback-add".format(self.portal_url)

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_required_params(self):
        """ """
        # vote is required
        res = self.anon_api_session.post(self.url, json={"honey": ""})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["message"], "Campo obbligatorio mancante: vote")

    def test_correctly_save_data(self):
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
        self.assertEqual(len(tool.search()), 1)

        # Anonymous cannot vote without access to document
        self.anon_api_session.post(
            self.url,
            json={
                "vote": 2,
                "comment": "i disagree",
                "honey": "",
                "content": self.private_document_path,
            },
        )
        transaction.commit()
        # Number of results did not increase, cause user is unauthorized to vote
        self.assertEqual(len(tool.search()), 1)

    def test_add_feedback_to_view(self):
        self.anon_api_session.post(
            self.url,
            json={
                "vote": 5,
                "comment": "Great login experience",
                "honey": "",
                "content": "login",
            },
        )
        transaction.commit()
        tool = getUtility(ICollectiveFeedbackStore)
        self.assertEqual(len(tool.search(query={"title": "login"})), 1)

    def test_store_only_known_fields(self):
        self.anon_api_session.post(
            self.url,
            json={
                "vote": "nok",
                "comment": "i disagree",
                "unknown": "mistery",
                "honey": "",
                "content": self.document_path,
            },
        )
        transaction.commit()
        tool = getUtility(ICollectiveFeedbackStore)
        res = tool.search()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]._attrs.get("unknown", None), None)
        self.assertEqual(res[0]._attrs.get("vote", None), "nok")
        self.assertEqual(res[0]._attrs.get("comment", None), "i disagree")

    def test_honeypot_is_required(self):
        res = self.anon_api_session.post(self.url, json={"content": self.document_path})
        self.assertEqual(res.status_code, 403)

        res = self.anon_api_session.post(
            self.url, json={"vote": "ok", "content": self.document_path}
        )
        self.assertEqual(res.status_code, 403)

        # HONEYPOT_FIELD is set in testing.py

        res = self.anon_api_session.post(
            self.url, json={"vote": "ok", "honey": "", "content": self.document_path}
        )
        self.assertEqual(res.status_code, 204)

        # this is compiled by a bot
        res = self.anon_api_session.post(
            self.url,
            json={"vote": "ok", "honey": "i'm a bot", "content": self.document_path},
        )
        self.assertEqual(res.status_code, 403)

    def test_add_feedback_to_allowed_and_disallowed_views(self):
        # Aggiunta di un feedback in una vista consentita
        res = self.anon_api_session.post(
            self.url,
            json={
                "vote": 5,
                "comment": "Great login experience",
                "honey": "",
                "content": "login",
            },
        )
        self.assertEqual(res.status_code, 204)
        transaction.commit()
        tool = getUtility(ICollectiveFeedbackStore)
        self.assertEqual(len(tool.search(query={"title": "login"})), 1)

        # Aggiunta di un feedback in una vista non consentita
        res = self.anon_api_session.post(
            self.url,
            json={
                "vote": 5,
                "comment": "Great admin experience",
                "honey": "",
                "content": "admin",
            },
        )
        self.assertEqual(res.status_code, 400)
        transaction.commit()
        self.assertEqual(len(tool.search(query={"title": "admin"})), 0)
