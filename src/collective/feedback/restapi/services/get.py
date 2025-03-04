from AccessControl import Unauthorized
from collective.feedback.interfaces import ICollectiveFeedbackStore
from copy import deepcopy
from datetime import datetime
from plone import api
from plone.restapi.batching import HypermediaBatch
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from six import StringIO
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import csv
import uuid


DEFAULT_SORT_KEY = "date"


@implementer(IPublishTraverse)
class FeedbackGet(Service):
    """Service for getting feedbacks"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, uid):
        # Consume any path segments after /@users as parameters
        self.params.append(uid)
        return self

    def reply(self):
        if self.params:
            # single object detail
            results = self.get_single_object_feedbacks(self.params[0])
        else:
            results = self.get_data()

        results = self.filter_unread(self.sort_results(results))

        batch = HypermediaBatch(self.request, results)
        data = {
            "@id": batch.canonical_url,
            "items": [self.fix_fields(data=x) for x in batch],
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            data["batching"] = links

        data["actions"] = {"can_delete_feedbacks": self.can_delete_feedbacks()}
        return data

    def sort_results(self, results):
        sort_on = self.request.get("sort_on")
        sort_order = self.request.get("sort_order", "")

        return sorted(
            results,
            key=lambda item: item.get(sort_on, DEFAULT_SORT_KEY),
            reverse=sort_order == "descending",
        )

    def filter_unread(self, results):
        unread = self.request.get("unread")

        if unread:
            return list(filter(lambda item: not item.get("read"), results))

        return results

    def can_delete_feedbacks(self):
        return api.user.has_permission("collective.feedback: Delete Feedbacks")

    def fix_fields(self, data):
        """
        Make data json compatible
        """
        for k, v in data.items():
            data[k] = json_compatible(v)
        return data

    def parse_query(self):
        query = deepcopy(self.request.form)
        query = unflatten_dotted_dict(query)
        res = {}
        if "sort_on" in query:
            res["sort_index"] = query["sort_on"]
            del query["sort_on"]
        if "sort_order" in query:
            order = query["sort_order"]
            reverse = True
            if order in ["asc", "ascending"]:
                reverse = False
            res["reverse"] = reverse
            del query["sort_order"]
        res["query"] = query
        return res

    def get_commented_obj(self, uid):
        """
        Return obj based on uid.
        """
        try:
            obj = api.content.get(UID=uid)
        except Unauthorized:
            return

        if not obj:
            return

        if not api.user.has_permission(
            "collective.feedback: Access Feedbacks", obj=obj
        ):
            # user does not have that permission on object
            return

        return obj

    def get_single_object_feedbacks(self, search_value):
        """
        Return data for single object
        """
        results = []
        commented_object = self.get_commented_obj(uid=search_value)
        if not commented_object:
            tool = getUtility(ICollectiveFeedbackStore)
            results = tool.search(query={"title": search_value})
            title = search_value
        else:
            tool = getUtility(ICollectiveFeedbackStore)
            results = tool.search(query={"uid": search_value})
            title = commented_object.title

        if not results:
            return results

        feedbacks = []
        for record in results:
            feedbacks.append(
                {
                    "uid": record._attrs.get("uid", ""),
                    "date": record._attrs.get("date", ""),
                    "vote": record._attrs.get("vote", ""),
                    "answer": record._attrs.get("answer", ""),
                    "comment": record._attrs.get("comment", ""),
                    "title": title,
                    "id": record.intid,
                    "read": record._attrs.get("read", ""),
                }
            )

        return feedbacks

    def sort_result(self, result):
        # sort
        sort_on = self.request.form.get("sort_on", "last_vote")
        sort_order = self.request.form.get("sort_order", "desc")
        reverse = sort_order.lower() in ["desc", "descending", "reverse"]
        if sort_on in ["vote", "title", "last_vote", "comments"]:
            result = sorted(result, key=lambda k: k[sort_on], reverse=reverse)

        return result

    def get_data(self):
        tool = getUtility(ICollectiveFeedbackStore)
        feedbacks = {}

        query = unflatten_dotted_dict(self.request.form)
        text = query.get("title", "")
        if text:
            query_res = tool.search(query={"title": text})
        else:
            query_res = tool.search()

        for feedback in query_res:
            uid = feedback._attrs.get("uid", "")
            # Some feedbacks are views, so no uid, use title
            # it should be unique
            if not uid:
                uid = feedback._attrs.get("title", "")
            date = feedback._attrs.get("date", "")
            vote = feedback._attrs.get("vote", "")

            if uid not in feedbacks:
                try:
                    uuid.UUID(uid)
                    valid_uuid = True
                except ValueError:
                    valid_uuid = False

                obj = None
                if valid_uuid:
                    obj = self.get_commented_obj(uid=uid)
                    if not obj and not api.user.has_permission(
                        "collective.feedback: Show Deleted Feedbacks"
                    ):
                        # only manager can list deleted object's reviews
                        continue

                new_data = {
                    "vote_num": 0,
                    "vote_sum": 0,
                    "comments": 0,
                    "title": feedback._attrs.get("title", ""),
                    "uid": uid,
                }

                if obj:
                    new_data["title"] = obj.Title()
                    new_data["url"] = obj.absolute_url()

                feedbacks[uid] = new_data

            # vote avg
            data = feedbacks[uid]
            data["vote_num"] += 1
            data["vote_sum"] += vote

            # Sign if page has unread comments
            data["has_unread"] = data.get(
                "has_unread", False
            ) or not feedback._attrs.get("read", False)

            # number of comment
            comment = feedback._attrs.get("comment", "")
            answer = feedback._attrs.get("answer", "")
            if comment or answer:
                data["comments"] += 1

            # last date comment
            if not data.get("last_vote", None):
                data["last_vote"] = date
            else:
                if data["last_vote"] < date:
                    data["last_vote"] = date

        pages_to_remove = []

        has_undread = query.get("has_unread", None)

        if has_undread in ("true", "false"):
            has_undread = not (has_undread == "false") and has_undread == "true"
        else:
            has_undread = None

        for uid, feedback in feedbacks.items():
            # avg calculation
            feedback["vote"] = feedback.pop("vote_sum") / feedback.pop("vote_num")

            # Use has_unread filter
            if has_undread is not None:
                if feedback["has_unread"] != has_undread:
                    pages_to_remove.append(uid)

        for uid in pages_to_remove:
            del feedbacks[uid]

        result = list(feedbacks.values())

        return self.sort_result(result)


class FeedbackGetCSV(FeedbackGet):
    """Service for getting feedbacks as csv file"""

    type = "feedbacks"

    def render(self):
        data = self.get_data()
        if isinstance(data, dict):
            if data.get("error", False):
                self.request.response.setStatus(500)
                return dict(
                    error=dict(
                        type="InternalServerError",
                        message="Unable export. Contact site manager.",
                    )
                )
        self.request.response.setHeader("Content-Type", "text/comma-separated-values")
        now = datetime.now()
        self.request.response.setHeader(
            "Content-Disposition",
            f'attachment; filename="{self.type}_{now.strftime("%d%m%Y-%H%M%S")}.csv"',
        )
        self.request.response.write(data)

    def plone2volto(self, url):
        portal_url = api.portal.get().absolute_url()
        frontend_domain = api.portal.get_registry_record(
            "volto.frontend_domain", default=""
        )
        if frontend_domain and url.startswith(portal_url):
            return url.replace(portal_url, frontend_domain, 1)
        return url

    def get_data(self):
        tool = getUtility(ICollectiveFeedbackStore)
        sbuf = StringIO()
        rows = []
        columns = ["title", "url", "vote", "comment", "date", "answer"]

        for item in tool.search():
            uid = item._attrs.get("uid", "")
            obj = self.get_commented_obj(uid=uid)

            data = {}
            for k, v in item.attrs.items():
                if k not in columns:
                    continue

                if isinstance(v, list):
                    v = ", ".join(v)

                if isinstance(v, int):
                    v = str(v)

                val = json_compatible(v)
                data[k] = val

            data["url"] = self.plone2volto(obj.absolute_url()) if obj else ""
            rows.append(data)

        writer = csv.DictWriter(sbuf, fieldnames=columns, delimiter=",")
        writer.writeheader()
        for row in rows:
            try:
                writer.writerow(row)
            except Exception:
                return {"error": True}

        res = sbuf.getvalue()
        sbuf.close()

        return res.encode()
