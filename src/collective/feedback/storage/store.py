# -*- coding: utf-8 -*-
from collective.feedback.interfaces import ICollectiveFeedbackStore
from datetime import datetime
from plone import api
from repoze.catalog.query import And
from repoze.catalog.query import Any
from repoze.catalog.query import Contains
from repoze.catalog.query import Eq
from souper.soup import get_soup
from souper.soup import Record
from zope.interface import implementer

import logging
import six


logger = logging.getLogger(__name__)


@implementer(ICollectiveFeedbackStore)
class CollectiveFeedbackStore(object):
    """Store class for collective.feedback catalog soup"""

    fields = ["uid", "url", "title", "comment", "vote", "answer", "date"]
    text_index = "title"
    indexes = ["title", "vote", "uid"]
    keyword_indexes = []

    @property
    def soup(self):
        return get_soup("feedback_soup", api.portal.get())

    def add(self, data):
        record = Record()
        for k, v in data.items():
            if k not in self.fields:
                logger.debug("[ADD] SKIP unkwnown field: {}".format(k))
                continue
            record.attrs[k] = v
        record.attrs["date"] = datetime.now()
        return self.soup.add(record)

    def length(self):
        return len([x for x in self.soup.data.values()])

    def search(self, query=None, sort_index="date", reverse=True):
        queries = []
        if query:
            queries = [
                self.parse_query_params(index, value)
                for index, value in query.items()
                if index in self.indexes and value
            ]
        if queries:
            return [
                x
                for x in self.soup.query(
                    And(*queries),
                    sort_index=sort_index,
                    reverse=reverse,
                )
            ]
        # return all data
        records = self.soup.data.values()
        if sort_index == "date":
            return sorted(
                records,
                key=lambda k: k.attrs[sort_index] or None,
                reverse=reverse,
            )
        return sorted(records, key=lambda k: k.attrs[sort_index] or "", reverse=reverse)

    def parse_query_params(self, index, value):
        """ """
        if index == self.text_index:
            return Contains(self.text_index, value)
            # return "'{}' in {}".format(value, self.text_index)
        elif index in self.keyword_indexes:
            return Any(index, value)
            # if isinstance(value, list):
            #     return "{} in any({})".format(index, value)
            # elif isinstance(value, six.text_type) or isinstance(value, str):
            #     return "{} in any('{}')".format(index, value)
        else:
            return Eq(index, value)
            if isinstance(value, int):
                return "{} == {}".format(index, value)
            else:
                return "{} == '{}'".format(index, value)

    def get_record(self, id):
        if isinstance(id, six.text_type) or isinstance(id, str):
            try:
                id = int(id)
            except ValueError as e:
                logger.exception(e)
                return None
        try:
            return self.soup.get(id)
        except KeyError as e:
            logger.exception(e)
            return None

    def update(self, id, data):
        try:
            record = self.soup.get(id)
        except KeyError:
            logger.error('[UPDATE] item with id "{}" not found.'.format(id))
            return {"error": "NotFound"}
        for k, v in data.items():
            if k not in self.fields:
                logger.debug("[UPDATE] SKIP unkwnown field: {}".format(k))

            else:
                record.attrs[k] = v
        self.soup.reindex(records=[record])

    def delete(self, id):
        try:
            record = self.soup.get(id)
        except KeyError:
            logger.error('[DELETE] Subscription with id "{}" not found.'.format(id))
            return {"error": "NotFound"}
        del self.soup[record]

    def clear(self):
        self.soup.clear()
