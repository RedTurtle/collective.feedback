# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.volto.blocksfield.field import BlocksField
from copy import deepcopy
from design.plone.policy.setuphandlers import disable_searchable_types
from design.plone.policy.setuphandlers import set_default_subsite_colors
from design.plone.policy.utils import create_default_blocks
from design.plone.policy.interfaces import IDesignPlonePolicySettings
from plone import api
from plone.app.upgrade.utils import installOrReinstallProduct
from plone.dexterity.utils import iterSchemata
from plone.registry.interfaces import IRegistry
from plone.restapi.behaviors import IBlocks
from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zope.component import getUtility
from zope.schema import getFields


import logging


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


def to_1100(context):
    installOrReinstallProduct(api.portal.get(), "souper.plone")
