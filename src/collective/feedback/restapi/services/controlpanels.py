# -*- coding: utf-8 -*-
from collective.feedback.controlpanels.settings import ICollectiveFeedbackSettings
from collective.feedback.controlpanels.settings import (
    ICollectiveFeedbackSettingsControlpanel,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, Interface)
@implementer(ICollectiveFeedbackSettingsControlpanel)
class CollectiveFeedbackSettings(RegistryConfigletPanel):
    schema = ICollectiveFeedbackSettings
    configlet_id = "CollectiveFeedbackSettings"
    configlet_category_id = "Products"
    schema_prefix = None
