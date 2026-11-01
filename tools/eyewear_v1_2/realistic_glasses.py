"""Realistic Glasses v1.2 -- testable preferences, scheduling and vision state.
Standalone diagnostic/gameplay prototype. No CAS outfit mutation or custom trait tuning.
"""
import os
import sys
import json
import traceback
from datetime import datetime

MOD_VERSION = "1.2"
CONTEXTS = ("day", "night", "school", "work", "cheer", "reading", "computer", "home", "outside")
PREFS = ("loves", "hates", "reluctant", "neutral")
CONDITIONS = ("normal", "myopia", "hyperopia", "astigmatism", "presbyopia", "anisometropia", "amblyopia", "strabismus", "color_vision_deficiency", "dry_eye", "allergic_conjunctivitis", "infectious_conjunctivitis", "blepharitis", "cataracts", "glaucoma", "keratoconus", "photophobia", "diplopia", "nystagmus", "retinal_disorders", "low_vision", "blindness", "digital_eye_strain")
_DATA = {"version": 1, "sims": {}}

def _directory():
    root = os.path.expanduser("~")
    for directory in (
        os.path.join(root, "Documents", "Electronic Arts", "The Sims 4"),
        os.path.join(root, "OneDrive", "Documents", "Electronic Arts", "The Sims 4"),
    ):
        if os.path.isdir(directory):
            return directory
    return None

def _path(name):
    base = _directory()
    return os.path.join(base, name) if base else None

def log(msg):
    try:
        path = _path("RealisticGlasses_Diagnostic.log")
        if path:
            with open(path, "a", encoding="utf-8") as handle:
                handle.write("[{}] v{} {}\n".format(datetime.now().isoformat(), MOD_VERSION, str(msg)))
    except Exception:
        pass

def _load():
    global _DATA
    try:
        filename = _path("RealisticGlasses_Profiles.json")
        if filename and os.path.isfile(filename):
            with open(filename, "r", encoding="utf-8") as f:
                found = json.load(f)
            if isinstance(found, dict) and isinstance(found.get("sims"), dict):
                _DATA = found
    except Exception:
        log("Profile read failed: " + traceback.format_exc())

def _save():
    try:
        filename = _path("RealisticGlasses_Profiles.json")
        if not filename:
            return False
        temp = filename + ".tmp"
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(_DATA, f, indent=2, sort_keys=True)
        os.replace(temp, filename)
        return True
    except Exception:
        log("Profile save failed: " + traceback.format_exc())
        return False

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

_load()
log("module imported under Python " + sys.version.split()[0])

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
            log("active sim lookup failed: " + traceback.format_exc())
            return None

    def _say(connection, message):
        sims4.commands.CheatOutput(connection)(str(message))
        log("console: " + str(message))

    def _with_sim(connection):
        sim = _active(connection)
        if sim is None:
            _say(connection, "Realistic Glasses: select a Sim in Live Mode")
            return None
        return _profile(sim)

    @sims4.commands.Command("eyewear.ping", command_type=sims4.commands.CommandType.Live)
    def ping(_connection=None):
        _say(_connection, "Realistic Glasses v1.2 loaded and commands working")
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
        _save()
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
        _save()
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
        _save()
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
        _save()
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
        _save()
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
        _save()
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

    log("registered: ping status preference prescribe glasses schedule context condition exam contexts help")
except Exception:
    log("Failed to register commands:\n" + traceback.format_exc())
