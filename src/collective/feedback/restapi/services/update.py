from collective.feedback.interfaces import ICollectiveFeedbackStore
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest, NotFound
from zope.component import getUtility
from zope.interface import alsoProvides, implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class FeedbackUpdate(Service):
    """
    Service for update feedback to object, you can only update `read` field
    """

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, id):
        # Consume any path segments after /@users as parameters
        self.params.append(id)
        return self

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        tool = getUtility(ICollectiveFeedbackStore)

        if self.params:
            id = self.params[0]

            comment = tool.get(id)

            if comment.get("error", "") == "NotFound":
                raise NotFound()

        form_data = json_body(self.request)

        self.validate_form(form_data=form_data)

        form_data = self.extract_data(form_data)

        try:
            res = tool.update(id, form_data)
        except ValueError as e:
            self.request.response.setStatus(500)
            return dict(
                error=dict(
                    type="InternalServerError",
                    message=getattr(e, "message", e.__str__()),
                )
            )

        if res == None:
            return self.reply_no_content()

        self.request.response.setStatus(500)

        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to add. Contact site manager.",
            )
        )

    def extract_data(sefl, form_data):
        return {"read": form_data.get("read")}

    def validate_form(self, form_data):
        """
        check all required fields and parameters
        """
        for field in ["read"]:
            value = form_data.get(field, "")
            if not value:
                raise BadRequest("Campo obbligatorio mancante: {}".format(field))
