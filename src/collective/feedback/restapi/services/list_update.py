from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest, NotFound
from zope.component import getUtility
from zope.interface import alsoProvides

from collective.feedback.interfaces import ICollectiveFeedbackStore


class FeedbacListkUpdate(Service):
    """
    Service for update feedback to object, you can only update `read` field
    """

    def __init__(self, context, request):
        super().__init__(context, request)

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        tool = getUtility(ICollectiveFeedbackStore)

        form_data = self.extract_data(json_body(self.request))

        for id, value in form_data.items():
            comment = tool.get(id)

            if comment.get("error", "") == "NotFound":
                raise NotFound()

            try:
                tool.update(id, value)
            except ValueError as e:
                self.request.response.setStatus(500)
                return dict(
                    error=dict(
                        type="InternalServerError",
                        message=getattr(e, "message", e.__str__()),
                    )
                )

        return form_data

    def extract_data(self, form_data):
        data = {}

        for id, value in form_data.items():
            try:
                self.validate_data(value)
                data[int(id)] = {"read": value.get("read")}
            except ValueError:
                raise BadRequest(f"Bad id={id} format provided")

        return data

    def validate_data(self, data):
        """
        check all required fields and parameters
        """
        for field in ["read"]:
            value = data.get(field, None)
            if value is None:
                raise BadRequest("Campo obbligatorio mancante: {}".format(field))
