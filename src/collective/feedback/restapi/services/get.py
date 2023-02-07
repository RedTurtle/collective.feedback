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


@implementer(IPublishTraverse)
class FeedbackGet(Service):
    """Service for getting feedbacks"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    def reply(self):
        if self.params:
            results = self.get_single_object_feedbacks(self.params[0])
            batch = HypermediaBatch(self.request, results)
            data = {
                "@id": batch.canonical_url,
                "items": [self.fix_fields(x, "date") for x in batch],
                "items_total": batch.items_total,
            }
            links = batch.links
            if links:
                data["batching"] = links
        else:
            results = self.get_data()
            batch = HypermediaBatch(self.request, results)
            data = {
                "@id": batch.canonical_url,
                "items": [self.fix_fields(x, "last_vote") for x in batch],
                "items_total": batch.items_total,
            }
            links = batch.links
            if links:
                data["batching"] = links

        return data

    def fix_fields(self, data, param):
        data[param] = json_compatible(data[param])
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

    def get_commented_obj(self, record):
        uid = record._attrs.get("uid", "")
        try:
            obj = api.content.get(UID=uid)
        except Unauthorized:
            return

        if not obj:
            return

        if not api.user.has_permission(
            "rer.customersatisfaction: Access Customer Satisfaction", obj=obj
        ):
            # user does not have that permission on object
            return

        return obj

    def get_single_object_feedbacks(self, uid):
        tool = getUtility(ICollectiveFeedbackStore)
        results = tool.search(query={"uid": uid})
        feedbacks = []

        for record in results:
            feedbacks.append(
                {
                    "uid": record._attrs.get("uid", ""),
                    "date": record._attrs.get("date", ""),
                    "vote": record._attrs.get("vote", ""),
                    "answer": record._attrs.get("answer", ""),
                    "comment": record._attrs.get("comment", ""),
                    "title": record._attrs.get("title", ""),
                }
            )

        return feedbacks

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
            date = feedback._attrs.get("date", "")
            vote = feedback._attrs.get("vote", "")

            if uid not in feedbacks:
                obj = self.get_commented_obj(record=feedback)
                if not obj:
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

        # avg calculation
        for uid, feedback in feedbacks.items():
            feedback["vote"] = feedback.pop("vote_sum") / feedback.pop("vote_num")

        result = list(feedbacks.values())

        # sort
        sort_on = self.request.form.get("sort_on", "last_vote")
        sort_order = self.request.form.get("sort_order", "desc")
        reverse = sort_order.lower() in ["desc", "descending", "reverse"]
        if sort_on in ["vote", "title", "last_vote", "comments"]:
            result = sorted(result, key=lambda k: k[sort_on], reverse=reverse)

        return result


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

    def get_data(self):
        tool = getUtility(ICollectiveFeedbackStore)
        sbuf = StringIO()
        rows = []
        columns = ["title", "url", "vote", "comment", "date", "answer"]

        for item in tool.search():
            obj = self.get_commented_obj(record=item)
            if not obj:
                continue

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

            data["url"] = obj.absolute_url()
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
