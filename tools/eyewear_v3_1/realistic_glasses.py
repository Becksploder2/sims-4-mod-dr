"""Realistic Glasses v3.1 -- testable preferences, scheduling and vision state.
Standalone diagnostic/gameplay prototype. No CAS outfit mutation or custom trait tuning.
"""
# Memory-only test: no filesystem, network, subprocess or executable operations.
MOD_VERSION = "3.1"
CONTEXTS = ("day", "night", "school", "work", "cheer", "sports", "reading", "homework", "computer", "crafting", "phone", "home", "outside")
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
            "glasses_part": None,
            "reading_part": None,
            "schedule_enabled": False,
            "schedule": [],
            "current_context": "home",
            "manual_override": None
        }
    record = _DATA["sims"][key]
    record.setdefault("glasses_part", None)
    record.setdefault("reading_part", None)
    record.setdefault("alternate_1_part", None)
    record.setdefault("alternate_2_part", None)
    record.setdefault("selected_pair", "regular")
    record.setdefault("pair_storage", {"regular": "assigned", "reading": "assigned", "alternate_1": "assigned", "alternate_2": "assigned"})
    record.setdefault("active_pair", "unknown")
    # Per-pair fit profiles are calibration preferences, not mesh deformation.
    record.setdefault("chain_fit_profiles", {})
    record.setdefault("universal_chain_style", None)
    record.setdefault("universal_chain_enabled", True)
    record.setdefault("universal_chain_only_active", False)
    record.setdefault("universal_chain_previous_part", None)
    record.setdefault("regular_chain_style", None)
    record.setdefault("reading_chain_style", None)
    record.setdefault("neck_pair_kind", None)
    record.setdefault("neck_glasses_part", None)
    record.setdefault("neck_previous_part", None)
    record.setdefault("neck_active", False)
    record.setdefault("neck_face_part", None)
    record.setdefault("last_action", "none")
    record.setdefault("sports_outfits", [])
    record.setdefault("cheer_outfits", [])
    record.setdefault("sports_glasses_enabled", True)
    record.setdefault("reading_auto", True)
    record.setdefault("use_regular_for_reading", False)
    record.setdefault("reading_activities", ["reading", "homework", "computer", "crafting", "phone"])
    record.setdefault("reading_active", False)
    record.setdefault("reading_previously_worn", None)
    record.setdefault("reading_manual_override", False)
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
        _say(_connection, "Realistic Glasses v3.1 loaded and commands working")
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



    @sims4.commands.Command("eyewear.last", command_type=sims4.commands.CommandType.Live)
    def last_action(_connection=None):
        p = _with_sim(_connection)
        if p is None:
            return False
        _say(_connection, "Last menu action: " + str(p.get("last_action", "none")))
        return True

    def _outfit_key(sim):
        category, index = sim.sim_info.get_current_outfit()
        return "{}:{}".format(int(category), int(index))

    @sims4.commands.Command("eyewear.outfit", command_type=sims4.commands.CommandType.Live)
    def set_outfit(kind: str = "sports", mode: str = "mark", _connection=None):
        sim = _active(_connection)
        if sim is None:
            _say(_connection, "Select a Sim in Live Mode")
            return False
        p = _profile(sim)
        if kind not in ("sports", "cheer") or mode not in ("mark", "unmark", "list"):
            _say(_connection, "Use eyewear.outfit sports|cheer mark|unmark|list")
            return False
        key = kind + "_outfits"
        if mode == "mark":
            p[key] = sorted(set(p[key]) | {_outfit_key(sim)})
        elif mode == "unmark":
            p[key] = sorted(set(p[key]) - {_outfit_key(sim)})
        _say(_connection, "{} outfits: {}".format(kind, ", ".join(p[key]) or "none"))
        return True

    @sims4.commands.Command("eyewear.sports", command_type=sims4.commands.CommandType.Live)
    def sports_rule(value: str = "on", _connection=None):
        p = _with_sim(_connection)
        if p is None:
            return False
        if value not in ("on", "off"):
            _say(_connection, "Use eyewear.sports on|off")
            return False
        p["sports_glasses_enabled"] = value == "on"
        _say(_connection, "Sports-event regular glasses rule: " + value)
        return True

    # CAS switching prototype; uses the selected Sim's current outfit only.
    GLASSES_SLOT = 11
    def outfit_change(sim, mode, chosen=None):
        from protocolbuffers import Outfits_pb2, S4Common_pb2
        from cas.cas import get_caspart_bodytype
        from bisect import bisect_left
        info=sim.sim_info
        category, index=info.get_current_outfit()
        if not info.has_outfit((category, index)):
            raise ValueError("Current outfit not found")
        live=info.get_outfit(category,index)
        bundle=Outfits_pb2.OutfitList()
        bundle.ParseFromString(info._base.outfits)
        target=next((x for x in bundle.outfits if x.outfit_id==live.outfit_id),None)
        if target is None:
            raise ValueError("Outfit data not found")
        parts=list(target.parts.ids)
        slots=list(target.body_types_list.body_types)
        shifts=list(target.part_shifts.color_shift)
        objects=list(target.object_ids.object_id)
        layers=list(target.layer_ids.layer_id)
        if any(len(arr)!=len(parts) for arr in (slots,shifts,objects,layers)):
            raise ValueError("Outfit arrays inconsistent; nothing changed")
        i=slots.index(GLASSES_SLOT) if GLASSES_SLOT in slots else -1
        previous=parts[i] if i>=0 else None
        if mode=="read":
            return False,previous
        if mode=="off":
            if i<0: return False,None
            for array in (parts,slots,shifts,objects,layers):
                del array[i]
        elif mode=="on":
            if chosen is None:
                raise ValueError("No glasses remembered: wear them in CAS, then use eyewear.capture")
            if int(get_caspart_bodytype(int(chosen)))!=GLASSES_SLOT:
                raise ValueError("Remembered part is not glasses")
            if i>=0:
                if parts[i]==chosen: return False,previous
                parts[i]=chosen
                shifts[i]=0x4000000000000000
                objects[i]=0
                layers[i]=0
            else:
                i=bisect_left(slots,GLASSES_SLOT)
                slots.insert(i,GLASSES_SLOT)
                parts.insert(i,chosen)
                shifts.insert(i,0x4000000000000000)
                objects.insert(i,0)
                layers.insert(i,0)
        else:
            raise ValueError("Unknown action")
        replacement=S4Common_pb2.IdList()
        replacement.ids.extend(parts)
        target.parts.CopyFrom(replacement)
        newslots=Outfits_pb2.BodyTypesList()
        newslots.body_types.extend(slots)
        target.body_types_list.CopyFrom(newslots)
        newshifts=Outfits_pb2.ColorShiftList()
        newshifts.color_shift.extend(shifts)
        target.part_shifts.CopyFrom(newshifts)
        newobjects=Outfits_pb2.ObjectIdsList()
        newobjects.object_id.extend(objects)
        target.object_ids.CopyFrom(newobjects)
        newlayers=Outfits_pb2.LayerIdsList()
        newlayers.layer_id.extend(layers)
        target.layer_ids.CopyFrom(newlayers)
        info._base.outfits=bundle.SerializeToString()
        # Mark the CAS outfit as changed and explicitly refresh the live Sim.
        # Silent refresh failures previously looked like successful switching.
        info.resend_outfits()
        info.on_outfit_generated(category, index)
        info.set_outfit_dirty(category)
        info.try_set_current_outfit((category, index))
        current = info.get_outfit(category, index)
        still_equipped = dict(zip(current.body_types, current.part_ids)).get(GLASSES_SLOT)
        if mode == "off" and still_equipped is not None:
            raise RuntimeError("Glasses remain equipped after outfit refresh: " + hex(still_equipped))
        if mode == "on" and still_equipped != chosen:
            raise RuntimeError("Glasses did not update in active outfit")
        return True,previous
    
    
    # A match must refer to a visually verified *matching* hanging accessory.
    # A necklace alone cannot be assumed to contain the selected face frames.
    # Asset creators may register verified (face_part, chain_style, hanging_part)
    # triples here after shipping the matching CAS necklace mesh.
    VERIFIED_HANGING_PAIRS = {}

    def chain_for_pair(profile, kind):
        """Return shared chain style first, preserving per-pair fallback."""
        if profile.get("universal_chain_enabled", True):
            chosen = profile.get("universal_chain_style")
            if chosen is not None:
                return chosen
        return profile.get(kind + "_chain_style")

    CHAIN_FIT_PRESETS = ("narrow", "standard", "wide", "extra_wide")

    def fit_profile(profile, kind):
        profiles = profile.setdefault("chain_fit_profiles", {})
        value = profiles.get(kind, "standard")
        return value if value in CHAIN_FIT_PRESETS else "standard"

    def set_fit_profile(profile, kind, value):
        if kind not in ("regular", "reading", "alternate_1", "alternate_2"):
            raise ValueError("Unknown glasses slot")
        if value not in CHAIN_FIT_PRESETS:
            raise ValueError("Unknown chain fit preset")
        profile.setdefault("chain_fit_profiles", {})[kind] = value

    # Only installed, visually vetted meshes belong here. No invented CAS IDs.
    VERIFIED_CHAIN_FIT_VARIANTS = {}

    def verified_fitted_neck_part(face_part, chain_style, fit):
        try:
            key = (int(face_part), int(chain_style), str(fit))
        except (ValueError, TypeError):
            return None
        return VERIFIED_CHAIN_FIT_VARIANTS.get(key)

    def verified_neck_part(face_part, chain_style):
        if face_part is None or chain_style is None:
            return None
        try:
            return VERIFIED_HANGING_PAIRS.get((int(face_part), int(chain_style)))
        except (ValueError, TypeError):
            return None

    # Slot 12 is the necklace CAS part (slot 11 is glasses).
    # Explicitly assigned accessory only: never convert arbitrary eyewear meshes.
    NECKLACE_SLOT = 12

    def necklace_part_change(sim, mode, chosen=None):
        from protocolbuffers import Outfits_pb2, S4Common_pb2
        from cas.cas import get_caspart_bodytype
        from bisect import bisect_left
        info = sim.sim_info
        category, index = info.get_current_outfit()
        if not info.has_outfit((category, index)):
            raise ValueError("Current outfit not found")
        live = info.get_outfit(category, index)
        bundle = Outfits_pb2.OutfitList()
        bundle.ParseFromString(info._base.outfits)
        target = next((x for x in bundle.outfits if x.outfit_id == live.outfit_id), None)
        if target is None:
            raise ValueError("Outfit data not found")
        parts = list(target.parts.ids)
        slots = list(target.body_types_list.body_types)
        shifts = list(target.part_shifts.color_shift)
        objects = list(target.object_ids.object_id)
        layers = list(target.layer_ids.layer_id)
        if any(len(a) != len(parts) for a in (slots, shifts, objects, layers)):
            raise ValueError("Outfit arrays inconsistent")
        i = slots.index(NECKLACE_SLOT) if NECKLACE_SLOT in slots else -1
        previous = parts[i] if i >= 0 else None
        if mode == "read":
            return False, previous
        if mode == "off":
            if i < 0:
                return False, None
            for a in (parts, slots, shifts, objects, layers):
                del a[i]
        elif mode == "on":
            if chosen is None or int(get_caspart_bodytype(int(chosen))) != NECKLACE_SLOT:
                raise ValueError("Assigned hanging glasses must be a necklace CAS part")
            if i >= 0:
                if parts[i] == chosen:
                    return False, previous
                parts[i] = chosen
                shifts[i] = 0x4000000000000000
                objects[i] = 0
                layers[i] = 0
            else:
                i = bisect_left(slots, NECKLACE_SLOT)
                slots.insert(i, NECKLACE_SLOT)
                parts.insert(i, chosen)
                shifts.insert(i, 0x4000000000000000)
                objects.insert(i, 0)
                layers.insert(i, 0)
        else:
            raise ValueError("Unknown necklace action")
        replacement = S4Common_pb2.IdList()
        replacement.ids.extend(parts)
        target.parts.CopyFrom(replacement)
        new_slots = Outfits_pb2.BodyTypesList()
        new_slots.body_types.extend(slots)
        target.body_types_list.CopyFrom(new_slots)
        new_shifts = Outfits_pb2.ColorShiftList()
        new_shifts.color_shift.extend(shifts)
        target.part_shifts.CopyFrom(new_shifts)
        new_objects = Outfits_pb2.ObjectIdsList()
        new_objects.object_id.extend(objects)
        target.object_ids.CopyFrom(new_objects)
        new_layers = Outfits_pb2.LayerIdsList()
        new_layers.layer_id.extend(layers)
        target.layer_ids.CopyFrom(new_layers)
        info._base.outfits = bundle.SerializeToString()
        info.resend_outfits()
        info.on_outfit_generated(category, index)
        info.set_outfit_dirty(category)
        info.try_set_current_outfit((category, index))
        return True, previous

    @sims4.commands.Command("eyewear.switchping",command_type=sims4.commands.CommandType.Live)
    def switch_ping(_connection=None):
        _say(_connection,"Realistic Glasses v1.5 CAS-switch test loaded")
        return True
    
    @sims4.commands.Command("eyewear.capture",command_type=sims4.commands.CommandType.Live)
    def capture(_connection=None):
        sim=_active(_connection)
        if sim is None:
            _say(_connection,"Select a Sim first")
            return False
        try:
            _,pid=outfit_change(sim,"read")
            if pid is None:
                _say(_connection,"No glasses equipped in current outfit; equip in CAS first")
                return False
            _profile(sim)["glasses_part"]=pid
            _say(_connection,"Captured glasses: "+hex(pid))
            return True
        except Exception as exc:
            _say(_connection,"Capture error: "+str(exc))
            return False
    
    @sims4.commands.Command("eyewear.takeoff",command_type=sims4.commands.CommandType.Live)
    def takeoff(_connection=None):
        sim=_active(_connection)
        if sim is None:
            _say(_connection,"Select a Sim first")
            return False
        try:
            modified,old=outfit_change(sim,"off")
            if old is not None:
                _profile(sim)["glasses_part"]=old
            _say(_connection,"Removed glasses" if modified else "No glasses in this outfit")
            return True
        except Exception as exc:
            _say(_connection,"Remove error: "+str(exc))
            return False
    
    @sims4.commands.Command("eyewear.puton",command_type=sims4.commands.CommandType.Live)
    def puton(_connection=None):
        sim=_active(_connection)
        if sim is None:
            _say(_connection,"Select a Sim first")
            return False
        try:
            modified,_=outfit_change(sim,"on",_profile(sim)["glasses_part"])
            _say(_connection,"Restored glasses" if modified else "Already wearing captured pair")
            return True
        except Exception as exc:
            _say(_connection,"Restore error: "+str(exc))
            return False
    
    @sims4.commands.Command("eyewear.switchstatus",command_type=sims4.commands.CommandType.Live)
    def status(_connection=None):
        sim=_active(_connection)
        if sim is None:
            _say(_connection,"Select a Sim first")
            return False
        try:
            _,now=outfit_change(sim,"read")
            previous=_profile(sim)["glasses_part"]
            _say(_connection,"Wearing: {} | Saved: {}".format(hex(now) if now else "none",hex(previous) if previous else "none"))
            return True
        except Exception as exc:
            _say(_connection,"Status error: "+str(exc))
            return False
    

    def _reading_part(profile):
        return profile["glasses_part"] if profile["use_regular_for_reading"] else profile["reading_part"]

    def _set_reading_mode(sim, active):
        profile = _profile(sim)
        if active:
            if not profile["reading_auto"] or profile["reading_manual_override"]:
                return False
            part = _reading_part(profile)
            if part is None:
                return False
            if profile["reading_active"]:
                return True
            _, previous = outfit_change(sim, "read")
            modified, _ = outfit_change(sim, "on", part)
            profile["reading_previously_worn"] = previous
            profile["reading_active"] = True
            return True
        if not profile["reading_active"]:
            return True
        # Restore previous eyewear and preserve non-eyewear CAS parts.
        previous = profile["reading_previously_worn"]
        if previous is None:
            outfit_change(sim, "off")
        else:
            outfit_change(sim, "on", previous)
        profile["reading_active"] = False
        profile["reading_previously_worn"] = None
        return True

    @sims4.commands.Command("eyewear.reading.capture", command_type=sims4.commands.CommandType.Live)
    def capture_reading(_connection=None):
        sim = _active(_connection)
        if sim is None:
            return False
        try:
            _, part = outfit_change(sim, "read")
            if part is None:
                _say(_connection, "Wear reading glasses in CAS first, then capture")
                return False
            _profile(sim)["reading_part"] = part
            _say(_connection, "Reading pair assigned: " + hex(part))
            return True
        except Exception as exc:
            _say(_connection, "Reading capture failed: " + str(exc))
            return False

    @sims4.commands.Command("eyewear.reading.auto", command_type=sims4.commands.CommandType.Live)
    def reading_auto(value: str = "on", _connection=None):
        p = _with_sim(_connection)
        if p is None or value not in ("on", "off"):
            return False
        p["reading_auto"] = value == "on"
        _say(_connection, "Automatic reading eyewear: " + value)
        return True

    @sims4.commands.Command("eyewear.reading.shared", command_type=sims4.commands.CommandType.Live)
    def shared_reading(value: str = "on", _connection=None):
        p = _with_sim(_connection)
        if p is None or value not in ("on", "off"):
            return False
        p["use_regular_for_reading"] = value == "on"
        _say(_connection, "Use regular glasses for reading: " + value)
        return True

    @sims4.commands.Command("eyewear.reading.activity", command_type=sims4.commands.CommandType.Live)
    def reading_activity(kind: str = "reading", phase: str = "start", _connection=None):
        sim = _active(_connection)
        if sim is None:
            return False
        p = _profile(sim)
        if kind not in ("reading", "homework", "computer", "crafting", "phone") or phase not in ("start", "end"):
            _say(_connection, "Use eyewear.reading.activity reading|homework|computer|crafting|phone start|end")
            return False
        if kind not in p["reading_activities"]:
            _say(_connection, "Activity disabled: " + kind)
            return False
        try:
            _set_reading_mode(sim, phase == "start")
            _say(_connection, "Reading activity: {} {}, active={}".format(kind, phase, p["reading_active"]))
            return True
        except Exception as exc:
            _say(_connection, "Reading activity error: " + str(exc))
            return False

    @sims4.commands.Command("eyewear.reading.trigger", command_type=sims4.commands.CommandType.Live)
    def reading_trigger(kind: str = "reading", value: str = "on", _connection=None):
        p = _with_sim(_connection)
        if p is None or kind not in ("reading", "homework", "computer", "crafting", "phone") or value not in ("on", "off"):
            return False
        chosen = set(p["reading_activities"])
        if value == "on":
            chosen.add(kind)
        else:
            chosen.discard(kind)
        p["reading_activities"] = sorted(chosen)
        _say(_connection, "Reading eyewear activities: " + ", ".join(p["reading_activities"]))
        return True

    @sims4.commands.Command("eyewear.reading.status", command_type=sims4.commands.CommandType.Live)
    def reading_status(_connection=None):
        p = _with_sim(_connection)
        if p is None:
            return False
        _say(_connection, "Reading auto={} shared={} part={} active={} activities={}".format(
            p["reading_auto"], p["use_regular_for_reading"], p["reading_part"],
            p["reading_active"], ",".join(p["reading_activities"])))
        return True

except Exception:
    raise
