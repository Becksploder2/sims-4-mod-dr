"""Realistic Glasses diagnostic only — does not modify Sims."""
import os
import sys
import traceback
from datetime import datetime

def log(message):
    root = os.path.expanduser("~")
    paths = [os.path.join(root, "Documents", "Electronic Arts", "The Sims 4"),
             os.path.join(root, "OneDrive", "Documents", "Electronic Arts", "The Sims 4")]
    for directory in paths:
        if os.path.isdir(directory):
            try:
                with open(os.path.join(directory, "RealisticGlasses_Diagnostic.log"), "a", encoding="utf-8") as f:
                    f.write("[{}] {}\n".format(datetime.now().isoformat(), message))
                return
            except Exception:
                pass

log("v1.0 compiled: module imported in Python " + sys.version.split()[0])
try:
    import sims4.commands
    import services

    @sims4.commands.Command("eyediag.ping", command_type=sims4.commands.CommandType.Live)
    def diagnostic_ping(_connection=None):
        log("eyediag.ping executed")
        sims4.commands.CheatOutput(_connection)("Realistic Glasses v1.0: command working")
        return True

    @sims4.commands.Command("eyediag.sim", command_type=sims4.commands.CommandType.Live)
    def diagnostic_sim(_connection=None):
        try:
            manager = services.client_manager()
            client = manager.get(_connection) if _connection is not None else None
            if client is None:
                client = manager.get_first_client()
            sim = client.active_sim if client is not None else None
            name = sim.full_name if sim is not None else "No active Sim"
            sims4.commands.CheatOutput(_connection)("Realistic Glasses: " + name)
            log("eyediag.sim: " + name)
            return True
        except Exception:
            log(traceback.format_exc())
            return False
    log("v1.0: registered eyediag.ping and eyediag.sim")
except Exception:
    log("v1.0: import/registration failed: " + traceback.format_exc())
