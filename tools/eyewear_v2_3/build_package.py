"""Prepare Sims 4 interaction tuning and string table input for trusted DBPF writer.
Run in GitHub Actions, not in the user's Mods folder.
"""
import json
from pathlib import Path
from xml.etree import ElementTree as ET

OUT=Path("build/eyewear_v2_3")
OUT.mkdir(parents=True, exist_ok=True)
RESOURCE_TYPE="0xE882D22F"
SNIPPET_TYPE="0x7DF2169C"
STBL_TYPE="0x220557DA"
ENTRIES=[
    (871640100001,"VisionEyewearRemember","Vision & Eyewear - Remember Glasses",0x6F772001),
    (871640100002,"VisionEyewearRemove","Vision & Eyewear - Take Off Glasses",0x6F772002),
    (871640100003,"VisionEyewearPutOn","Vision & Eyewear - Put On Glasses",0x6F772003),
    (871640100004,"VisionEyewearRememberReading","Vision & Eyewear - Assign Reading Glasses",0x6F772004),
    (871640100005,"VisionEyewearPutOnReading","Vision & Eyewear - Put On Reading Glasses",0x6F772005),
    (871640100006,"VisionEyewearMarkSports","Vision & Eyewear - Mark Sports Outfit",0x6F772006),
    (871640100007,"VisionEyewearMarkCheer","Vision & Eyewear - Mark Cheer Outfit",0x6F772007),
    (871640100008,"VisionEyewearStoreInInventory","Vision & Eyewear - Store Glasses in Inventory (Experimental)",0x6F772008),
]
resources=[]
strings={}
for instance,cls,label,string_key in ENTRIES:
    root=ET.Element("I",{
        "c":cls,"i":"interaction","m":"eyewear_menu",
        "n":"WPS_"+cls,"s":str(instance)})
    ET.SubElement(root,"V",{"t":"disabled","n":"_saveable"})
    ET.SubElement(root,"T",{"n":"category"}).text="0"
    ET.SubElement(root,"T",{"n":"display_name"}).text="0x{:08X}".format(string_key)
    progress=ET.SubElement(root,"U",{"n":"progress_bar_enabled"})
    ET.SubElement(progress,"T",{"n":"bar_enabled"}).text="False"
    ET.SubElement(root,"E",{"n":"target_type"}).text="OBJECT"
    name="{}_{}.xml".format(instance,cls)
    path=OUT/name
    path.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(root,encoding="utf-8"))
    ET.parse(str(path))
    strings["0x{:08X}".format(string_key)]=label
    resources.append({"type":RESOURCE_TYPE,"group":"0x00000000","instance":"0x{:016X}".format(instance),"path":name,"compression":"off"})

snippet_id=871640100099
root=ET.Element("I",{"c":"XmlInjector","i":"snippet","m":"xml_injector.snippet","n":"WPS_RealisticGlasses_SimInjection","s":str(snippet_id)})
listing=ET.SubElement(root,"L",{"n":"add_interactions_to_sims"})
for instance, cls, label, key in ENTRIES:
    ET.SubElement(listing,"T").text=str(instance)
snippet_name="xml_injector.xml"
(OUT/snippet_name).write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\\n'.replace(b'\\n',b'\n')+ET.tostring(root,encoding="utf-8"))
ET.parse(str(OUT/snippet_name))
resources.append({"type":SNIPPET_TYPE,"group":"0x00000000","instance":"0x{:016X}".format(snippet_id),"path":snippet_name,"compression":"off"})
(OUT/"strings.json").write_text(json.dumps({"strings":strings},indent=2),encoding="utf-8")
resources.append({"type":STBL_TYPE,"group":"0x00000000","instance":"0x0000000087714071","path":"eyewear.stbl","compression":"off"})
(OUT/"manifest.json").write_text(json.dumps({"resources":resources},indent=2),encoding="utf-8")
print("Prepared {} interaction tunings and string table manifest".format(len(ENTRIES)))
