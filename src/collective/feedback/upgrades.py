# -*- coding: utf-8 -*-
import logging

from plone import api
from plone.app.upgrade.utils import installOrReinstallProduct

logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-collective.feedback:default"


def update_profile(context, profile, run_dependencies=True):
    context.runImportStepFromProfile(DEFAULT_PROFILE, profile, run_dependencies)


def update_types(context):
    update_profile(context, "typeinfo")


def update_rolemap(context):
    update_profile(context, "rolemap")


def update_registry(context):
    update_profile(context, "plone.app.registry", run_dependencies=False)


def update_catalog(context):
    update_profile(context, "catalog")


def update_controlpanel(context):
    update_profile(context, "controlpanel")


def update_actions(context):
    update_profile(context, "actions")


def to_1100(context):
    installOrReinstallProduct(api.portal.get(), "souper.plone")
    context.runAllImportStepsFromProfile("profile-collective.feedback:to_1100")

    # remove broken action
    if "feedback-dashboard" in context.portal_actions.user:
        del context.portal_actions.user["feedback-dashboard"]
