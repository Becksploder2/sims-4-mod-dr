"""Realistic Glasses v1.5 — visible current-outfit switching test, no disk writes."""
import sims4.commands
import services
from protocolbuffers import Outfits_pb2, S4Common_pb2
from cas.cas import get_caspart_bodytype
from bisect import bisect_left

GLASSES_SLOT=11
MEMORY={}

def output(connection, message):
    sims4.commands.CheatOutput(connection)(str(message))

def current_sim(connection):
    manager=services.client_manager()
    client=manager.get(connection) if connection is not None else None
    if client is None:
        client=manager.get_first_client()
    return client.active_sim if client is not None else None

def saved(sim):
    return MEMORY.setdefault(str(sim.sim_info.sim_id), {'glasses':None})

def outfit_change(sim, mode, chosen=None):
    info=sim.sim_info
    category, index=info.get_current_outfit()
    if not info.has_outfit(category,index):
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
    info.resend_outfits()
    return True,previous

@sims4.commands.Command("eyewear.ping",command_type=sims4.commands.CommandType.Live)
def ping(_connection=None):
    output(_connection,"Realistic Glasses v1.5 CAS-switch test loaded")
    return True

@sims4.commands.Command("eyewear.capture",command_type=sims4.commands.CommandType.Live)
def capture(_connection=None):
    sim=current_sim(_connection)
    if sim is None:
        output(_connection,"Select a Sim first")
        return False
    try:
        _,pid=outfit_change(sim,"read")
        if pid is None:
            output(_connection,"No glasses equipped in current outfit; equip in CAS first")
            return False
        saved(sim)["glasses"]=pid
        output(_connection,"Captured glasses: "+hex(pid))
        return True
    except Exception as exc:
        output(_connection,"Capture error: "+str(exc))
        return False

@sims4.commands.Command("eyewear.takeoff",command_type=sims4.commands.CommandType.Live)
def takeoff(_connection=None):
    sim=current_sim(_connection)
    if sim is None:
        output(_connection,"Select a Sim first")
        return False
    try:
        modified,old=outfit_change(sim,"off")
        if old is not None:
            saved(sim)["glasses"]=old
        output(_connection,"Removed glasses" if modified else "No glasses in this outfit")
        return True
    except Exception as exc:
        output(_connection,"Remove error: "+str(exc))
        return False

@sims4.commands.Command("eyewear.puton",command_type=sims4.commands.CommandType.Live)
def puton(_connection=None):
    sim=current_sim(_connection)
    if sim is None:
        output(_connection,"Select a Sim first")
        return False
    try:
        modified,_=outfit_change(sim,"on",saved(sim)["glasses"])
        output(_connection,"Restored glasses" if modified else "Already wearing captured pair")
        return True
    except Exception as exc:
        output(_connection,"Restore error: "+str(exc))
        return False

@sims4.commands.Command("eyewear.status",command_type=sims4.commands.CommandType.Live)
def status(_connection=None):
    sim=current_sim(_connection)
    if sim is None:
        output(_connection,"Select a Sim first")
        return False
    try:
        _,now=outfit_change(sim,"read")
        previous=saved(sim)["glasses"]
        output(_connection,"Wearing: {} | Saved: {}".format(hex(now) if now else "none",hex(previous) if previous else "none"))
        return True
    except Exception as exc:
        output(_connection,"Status error: "+str(exc))
        return False
