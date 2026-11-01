"""Realistic Glasses v1.3 -- testable preferences, scheduling and vision state.
Standalone diagnostic/gameplay prototype. No CAS outfit mutation or custom trait tuning.
"""
# Memory-only test: no filesystem, network, subprocess or executable operations.
MOD_VERSION = "1.3"
CONTEXTS = ("day", "night", "school", "work", "cheer", "reading", "computer", "home", "outside")
PREFS = ("loves", "hates", "reluctant", "neutral")
CONDITIONS = ("normal", "myopia", "hyperopia", "astigmatism", "presbyopia", "anisometropia", "amblyopia", "strabismus", "color_vision_deficiency", "dry_eye", "allergic_conjunctivitis", "infectious_conjunctivitis", "blepharitis", "cataracts", "glaucoma", "keratoconus", "photophobia", "diplopia", "nystagmus", "retinal_disorders", "low_vision", "blindness", "digital_eye_strain")
_DATA = {"version": 1, "sims": {}}

def _profile_key(sim):
    try:
        return str(sim.sim_info.sim_id)
    except Exception:
        return str(sim.id)

def _profile(sim):
    key = _profile_key(sim)
    if key not in _DATA["sims"]:
        _DATA["sims"][key] = {
            "sim_name": str(sim.full_name),
            "preference": "neutral",
            "diagnosis": "undetermined",
            "conditions": [],
            "examination_complete": False,
            "corrected": 95,
            "uncorrected": 45,
            "wearing": False,
            "schedule_enabled": False,
            "schedule": [],
            "current_context": "home",
            "manual_override": None
        }
    record = _DATA["sims"][key]
    record.setdefault("conditions", [])
    record.setdefault("examination_complete", False)
    return record

def _functional(profile):
    return profile["corrected"] if profile["wearing"] else profile["uncorrected"]

def _sync(profile):
    if profile["manual_override"] is not None:
        profile["wearing"] = bool(profile["manual_override"])
    elif profile["schedule_enabled"]:
        profile["wearing"] = profile["current_context"] in profile["schedule"]

def _status(profile):
    return ("{} | {} | glasses={} | functional vision={} | context={} | schedule={} | enabled={}"
            .format(profile["sim_name"] + " [conditions=" + (",".join(profile["conditions"]) or "none") + "]", profile["preference"], "on" if profile["wearing"] else "off",
                    _functional(profile), profile["current_context"],
                    ",".join(profile["schedule"]) or "none", profile["schedule_enabled"]))


try:
    import sims4.commands
    import services

    def _active(connection):
        try:
            manager = services.client_manager()
            client = manager.get(connection) if connection is not None else None
            if client is None:
                client = manager.get_first_client()
            return client.active_sim if client is not None else None
        except Exception:
            return None

    def _say(connection, message):
        sims4.commands.CheatOutput(connection)(str(message))

    def _with_sim(connection):
        sim = _active(connection)
        if sim is None:
            _say(connection, "Realistic Glasses: select a Sim in Live Mode")
            return None
        return _profile(sim)

    @sims4.commands.Command("eyewear.ping", command_type=sims4.commands.CommandType.Live)
    def ping(_connection=None):
        _say(_connection, "Realistic Glasses v1.3 loaded and commands working")
        return True

    @sims4.commands.Command("eyewear.status", command_type=sims4.commands.CommandType.Live)
    def status(_connection=None):
        profile = _with_sim(_connection)
        if profile is None:
            return False
        _say(_connection, _status(profile))
        return True

    @sims4.commands.Command("eyewear.preference", command_type=sims4.commands.CommandType.Live)
    def preference(value: str = "neutral", _connection=None):
        profile = _with_sim(_connection)
        if profile is None:
            return False
        value = value.lower().strip()
        if value not in PREFS:
            _say(_connection, "Use: eyewear.preference loves|hates|reluctant|neutral")
            return False
        profile["preference"] = value
        _say(_connection, "Glasses preference: " + value)
        return True

    @sims4.commands.Command("eyewear.prescribe", command_type=sims4.commands.CommandType.Live)
    def prescribe(uncorrected: int = 45, corrected: int = 95, _connection=None):
        profile = _with_sim(_connection)
        if profile is None:
            return False
        if not (0 <= uncorrected <= 100 and 0 <= corrected <= 100):
            _say(_connection, "Vision scores must be 0 to 100")
            return False
        profile["uncorrected"] = int(uncorrected)
        profile["corrected"] = int(corrected)
        _say(_connection, "Vision profile set: uncorrected {} corrected {}".format(uncorrected, corrected))
        return True

    @sims4.commands.Command("eyewear.glasses", command_type=sims4.commands.CommandType.Live)
    def glasses(value: str = "off", _connection=None):
        profile = _with_sim(_connection)
        if profile is None:
            return False
        value = value.lower().strip()
        if value not in ("on", "off", "auto"):
            _say(_connection, "Use: eyewear.glasses on|off|auto")
            return False
        profile["manual_override"] = None if value == "auto" else (value == "on")
        if value != "auto":
            profile["wearing"] = value == "on"
        else:
            _sync(profile)
        _say(_connection, "Simulated glasses state: " + ("on" if profile["wearing"] else "off") +
             " (does NOT modify visible CAS glasses)")
        return True

    @sims4.commands.Command("eyewear.schedule", command_type=sims4.commands.CommandType.Live)
    def schedule(context: str = "cheer", value: str = "on", _connection=None):
        profile = _with_sim(_connection)
        if profile is None:
            return False
        context = context.lower().strip()
        value = value.lower().strip()
        if context == "enable":
            profile["schedule_enabled"] = True
            profile["manual_override"] = None
        elif context == "disable":
            profile["schedule_enabled"] = False
        elif context in CONTEXTS and value in ("on", "off"):
            profile["schedule"] = sorted((set(profile["schedule"]) | {context})
                                         if value == "on" else (set(profile["schedule"]) - {context}))
        else:
            _say(_connection, "Use: eyewear.schedule cheer on | eyewear.schedule enable | eyewear.schedule disable")
            return False
        _sync(profile)
        _say(_connection, _status(profile))
        return True

    @sims4.commands.Command("eyewear.context", command_type=sims4.commands.CommandType.Live)
    def context(value: str = "home", _connection=None):
        profile = _with_sim(_connection)
        if profile is None:
            return False
        value = value.lower().strip()
        if value not in CONTEXTS:
            _say(_connection, "Contexts: " + ", ".join(CONTEXTS))
            return False
        profile["current_context"] = value
        _sync(profile)
        _say(_connection, _status(profile))
        return True


    @sims4.commands.Command("eyewear.condition", command_type=sims4.commands.CommandType.Live)
    def condition(value: str = "myopia", mode: str = "add", _connection=None):
        profile = _with_sim(_connection)
        if profile is None:
            return False
        value = value.lower().strip()
        mode = mode.lower().strip()
        if value not in CONDITIONS or mode not in ("add", "remove"):
            _say(_connection, "Conditions: " + ", ".join(CONDITIONS) + " | modes: add/remove")
            return False
        selected = set(profile["conditions"])
        if mode == "remove":
            selected.discard(value)
        elif value == "normal":
            selected = set()
        else:
            selected.discard("normal")
            selected.add(value)
        profile["conditions"] = sorted(selected)
        profile["examination_complete"] = True
        profile["diagnosis"] = ", ".join(profile["conditions"]) or "normal"
        _say(_connection, "Vision diagnoses: " + profile["diagnosis"])
        return True

    @sims4.commands.Command("eyewear.exam", command_type=sims4.commands.CommandType.Live)
    def exam(_connection=None):
        profile = _with_sim(_connection)
        if profile is None:
            return False
        if not profile["examination_complete"]:
            _say(_connection, "Eye exam: no diagnosis yet. Use eyewear.condition myopia to assign a simulated diagnosis.")
            return True
        _say(_connection, "Eye exam results: " + profile["diagnosis"] +
             "; corrected=" + str(profile["corrected"]) +
             "; uncorrected=" + str(profile["uncorrected"]))
        return True

    @sims4.commands.Command("eyewear.contexts", command_type=sims4.commands.CommandType.Live)
    def list_contexts(_connection=None):
        _say(_connection, "Available schedule contexts: " + ", ".join(CONTEXTS))
        return True

    @sims4.commands.Command("eyewear.help", command_type=sims4.commands.CommandType.Live)
    def help_command(_connection=None):
        _say(_connection, "Commands: eyewear.ping / status / preference hates|loves / condition myopia / exam / prescribe 45 95 / glasses on|off|auto / schedule cheer on / schedule enable / context cheer / contexts")
        return True

except Exception:
    raise
