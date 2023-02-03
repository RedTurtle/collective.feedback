# -*- coding: utf-8 -*-
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from souper.interfaces import ICatalogFactory
from souper.soup import NodeAttributeIndexer
from souper.soup import NodeTextIndexer
from zope.interface import implementer


@implementer(ICatalogFactory)
class FeedbackSoupCatalogFactory(object):
    def __call__(self, context):
        catalog = Catalog()

        text_indexer = NodeTextIndexer(["title"])
        catalog["title"] = CatalogTextIndex(text_indexer)

        vote_indexer = NodeAttributeIndexer("vote")
        catalog["vote"] = CatalogFieldIndex(vote_indexer)

        uid_indexer = NodeAttributeIndexer("uid")
        catalog["uid"] = CatalogFieldIndex(uid_indexer)

        date_indexer = NodeAttributeIndexer("date")
        catalog["date"] = CatalogFieldIndex(date_indexer)

        return catalog
