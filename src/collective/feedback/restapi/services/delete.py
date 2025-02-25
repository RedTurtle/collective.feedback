from collective.feedback.interfaces import ICollectiveFeedbackStore
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import uuid


@implementer(IPublishTraverse)
class FeedbackDelete(Service):
    """Service for delete feedbacks"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        tool = getUtility(ICollectiveFeedbackStore)

        if self.params:
            search_value = self.params[0]
            try:
                uuid.UUID(search_value)
                valid_uuid = True
            except ValueError:
                valid_uuid = False

            feedbacks = (
                tool.search(query={"uid": search_value})
                if valid_uuid
                else tool.search(query={"title": search_value})
            )
            for feedback in feedbacks:
                res = tool.delete(id=feedback.intid)
                if not res:
                    continue
                if res.get("error", "") == "NotFound":
                    raise BadRequest(
                        'Unable to find item with id "{}"'.format(search_value)
                    )
                self.request.response.setStatus(500)
                return dict(
                    error=dict(
                        type="InternalServerError",
                        message="Unable to delete item. Contact site manager.",
                    )
                )

        else:
            tool.clear()

        return self.reply_no_content()
