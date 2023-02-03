from collective.feedback.interfaces import ICollectiveFeedbackStore
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides


class FeedbackDelete(Service):
    """Service for delete feedbacks"""

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        tool = getUtility(ICollectiveFeedbackStore)

        # import pdb
        #
        # pdb.set_trace()
        if self.id:
            try:
                self.id = int(self.id)
            except ValueError:
                raise BadRequest("Id should be a number.")

            res = tool.delete(id=self.id)
            if not res:
                return self.reply_no_content()
        else:
            tool.clear()
            return self.reply_no_content()

        if not res:
            return self.reply_no_content()
        if res.get("error", "") == "NotFound":
            raise BadRequest('Unable to find item with id "{}"'.format(self.id))
        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to delete item. Contact site manager.",
            )
        )
