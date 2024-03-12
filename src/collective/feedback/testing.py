from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing.zope import WSGI_SERVER_FIXTURE

import collective.feedback
import collective.honeypot
import collective.honeypot.config
import plone.restapi
import souper.plone


collective.honeypot.config.EXTRA_PROTECTED_ACTIONS = set(["feedback-add"])
collective.honeypot.config.HONEYPOT_FIELD = "honey"


class TestLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.honeypot)
        self.loadZCML(package=souper.plone)
        self.loadZCML(package=collective.feedback)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.feedback:default")


FIXTURE = TestLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="CollectiveFeedbackLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name="CollectiveFeedbackLayer:FunctionalTesting",
)

RESTAPI_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="CollectiveFeedbackLayer:RestAPITesting",
)
