# -*- coding: utf-8 -*-
from collective.feedback import _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels.interfaces import IControlpanel
from zope.interface import Interface
from zope.schema import List
from zope.schema import TextLine


class ICollectiveFeedbackSettingsControlpanel(IControlpanel):
    """ """


class ICollectiveFeedbackSettings(Interface):
    allowed_feedback_view = List(
        title=_(
            "allowed_feedback_view_label",
            default="Vista su cui è possibile lasciare dei feedback",
        ),
        required=True,
        default=[
            "Login/Logout",
            "Ricerca",
            "Search",
            "Le mie prenotazioni",
            "My bookings",
            "Prenotazione appuntamento",
            "Appointment booking",
            "Export appuntamenti",
            "Export bookings",
            "Area personale",
            "Personal area",
            "Area operatore",
            "Operator area",
        ],
        value_type=TextLine(),
    )


class CollectiveFeedbackControlPanelForm(RegistryEditForm):
    schema = ICollectiveFeedbackSettings
    id = "collective-feedback-control-panel"
    label = _("Impostazioni Collective Feedback")


class CollectiveFeedbackControlPanelView(ControlPanelFormWrapper):
    """ """

    form = CollectiveFeedbackControlPanelForm
