# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.feedback
import plone.app.dexterity
import plone.restapi
import souper.plone


class CollectiveFeedbackLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.feedback)
        self.loadZCML(package=souper.plone)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.feedback:default")


COLLECTIVE_FEEDBACK_FIXTURE = CollectiveFeedbackLayer()


COLLECTIVE_FEEDBACK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_FEEDBACK_FIXTURE,),
    name="CollectiveFeedbackLayer:IntegrationTesting",
)


COLLECTIVE_FEEDBACK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FEEDBACK_FIXTURE,),
    name="CollectiveFeedbackLayer:FunctionalTesting",
)


COLLECTIVE_FEEDBACK_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_FEEDBACK_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveFeedbackLayer:AcceptanceTesting",
)
