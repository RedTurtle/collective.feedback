from collective.feedback.controlpanels.settings import ICollectiveFeedbackSettings
from collective.feedback.interfaces import ICollectiveFeedbackStore
from collective.feedback.restapi.services import looks_like_path
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides


class FeedbackAdd(Service):
    """
    Service for add feedback to object
    """

    store = ICollectiveFeedbackStore

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.allowed_views = api.portal.get_registry_record(
            "allowed_feedback_view",
            interface=ICollectiveFeedbackSettings,
            default=False,
        )
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

    def check_allowed_views(self, value):
        for allowed_view in self.allowed_views:
            if value == allowed_view:
                return True
            if looks_like_path(allowed_view):
                if allowed_view.endswith("/"):
                    check_path = allowed_view
                else:
                    check_path = allowed_view + "/"
                return value.startswith(check_path)
        return False

    def extract_data(self, form_data):
        path = form_data.pop("content")

        if self.check_allowed_views(path):
            form_data.update({"title": path})
        else:
            portal = api.portal.get()
            contextual_path = "/" + portal.id + path
            context = api.content.get(path=contextual_path)
            if context:
                form_data.update({"uid": context.UID()})
                form_data.update({"title": context.Title()})
            else:
                raise BadRequest(f"Object with path {path} not found.")
        return form_data
