from collective.feedback.interfaces import ICollectiveFeedbackStore
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
        for field in ["vote"]:
            value = form_data.get(field, "")
            if not value:
                raise BadRequest("Campo obbligatorio mancante: {}".format(field))

    def extract_data(self, form_data):
        context_state = api.content.get_view(
            context=self.context,
            request=self.request,
            name="plone_context_state",
        )
        context = context_state.canonical_object()
        form_data.update({"uid": context.UID()})
        form_data.update({"title": context.Title()})
        return form_data
