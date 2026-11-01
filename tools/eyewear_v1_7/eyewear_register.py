"""Register three Vision & Eyewear interactions on Sim instances."""
from sims4communitylib.services.interactions.interaction_registration_service import CommonInteractionRegistry, CommonInteractionType, CommonScriptObjectInteractionHandler
from sims4communitylib.utils.common_type_utils import CommonTypeUtils

INTERACTIONS = (871640100001, 871640100002, 871640100003)

@CommonInteractionRegistry.register_interaction_handler(CommonInteractionType.ON_SCRIPT_OBJECT_LOAD)
class _RegisterVisionEyewear(CommonScriptObjectInteractionHandler):
    @property
    def interactions_to_add(self):
        return INTERACTIONS

    def should_add(self, script_object, *args, **kwargs):
        return CommonTypeUtils.is_sim_instance(script_object)
