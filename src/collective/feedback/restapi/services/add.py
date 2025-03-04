from collective.feedback.controlpanels.settings import ICollectiveFeedbackSettings
from collective.feedback.interfaces import ICollectiveFeedbackStore
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides

import re


class FeedbackAdd(Service):
    """
    Service for add feedback to object
    """

    store = ICollectiveFeedbackStore

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        form_data = json_body(self.request)
        self.validate_form(form_data=form_data)
        data = self.extract_data(form_data=form_data)
        tool = getUtility(self.store)
        try:
            res = tool.add(data)
        except ValueError as e:
            self.request.response.setStatus(500)
            return dict(
                error=dict(
                    type="InternalServerError",
                    message=getattr(e, "message", e.__str__()),
                )
            )

        if res:
            return self.reply_no_content()

        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to add. Contact site manager.",
            )
        )

    def validate_form(self, form_data):
        """
        check all required fields and parameters
        """
        for field in ["vote", "content"]:
            value = form_data.get(field, "")
            if not value:
                raise BadRequest("Campo obbligatorio mancante: {}".format(field))

    def looks_like_path(self, string):
        return bool(re.match(r"^(/|/[^\s<>:\"|?*]+.*)$", string))

    def extract_data(self, form_data):
        path = form_data.pop("content")
        if self.looks_like_path(path):
            portal = api.portal.get()
            contextual_path = "/" + portal.id + path
            context = api.content.get(path=contextual_path)
            if not context:
                raise BadRequest(f"Object with path {contextual_path} not found.")

            form_data.update({"uid": context.UID()})
            form_data.update({"title": context.Title()})
        else:
            allowed_view = api.portal.get_registry_record(
                "allowed_feedback_view",
                interface=ICollectiveFeedbackSettings,
                default=False,
            )
            if path not in allowed_view:
                raise BadRequest(f"View non consentita: {path}")

            form_data.update({"title": path})

        return form_data
