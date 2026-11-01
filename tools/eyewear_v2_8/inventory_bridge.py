"""Realistic Glasses inventory bridge. No external library or disk writes.

Requires an actual packaged inventory-compatible glasses-case object definition.
Intentionally has no fabricated or borrowed gameplay object ID.
"""
CASE_DEFINITION_ID = None

def store_glasses_case(sim):
    """Create a real inventory object; return (success, object, reason).

    Does not remove CAS glasses. Caller removes them only after a case is added.
    """
    if CASE_DEFINITION_ID is None:
        return False, None, "No licensed, tested Glasses Case object definition is bundled yet"
    try:
        from objects.system import create_object
        inventory = getattr(sim, "inventory_component", None)
        if inventory is None:
            return False, None, "Sim does not have an available personal inventory"
        case = create_object(CASE_DEFINITION_ID)
        if case is None:
            return False, None, "Glasses Case object could not be created"
        try:
            if not inventory.player_try_add_object(case):
                case.destroy()
                return False, None, "Personal inventory rejected the case"
            return True, case, ""
        except Exception:
            case.destroy()
            raise
    except Exception as exc:
        return False, None, "{}: {}".format(type(exc).__name__, str(exc))

def rollback_case(case):
    if case is None:
        return
    try:
        case.destroy()
    except Exception:
        pass
