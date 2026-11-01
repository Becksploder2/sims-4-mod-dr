"""Prepare Sims 4 interaction tuning and string table input for trusted DBPF writer.
Run in GitHub Actions, not in the user's Mods folder.
"""
import json
from pathlib import Path
from xml.etree import ElementTree as ET

OUT=Path("build/eyewear_v3_2")
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
    (871640100009,"VisionEyewearUseRegularForReading","Vision & Eyewear - Toggle Use Regular Glasses for Reading",0x6F772009),
    (871640100010,"VisionEyewearAssignNeck","Vision & Eyewear - Assign Regular Chain Style (Selected Necklace)",0x6F77200A),
    (871640100011,"VisionEyewearHangNeck","Vision & Eyewear - Hang Active Glasses (Matching Frames Only)",0x6F77200B),
    (871640100012,"VisionEyewearPutOnFromNeck","Vision & Eyewear - Put Glasses On From Neck",0x6F77200C),
    (871640100013,"VisionEyewearFaceAndNeck","Vision & Eyewear - Wear Face Glasses and Neck Pair",0x6F77200D),
    (871640100014,"VisionEyewearRemoveNeck","Vision & Eyewear - Remove Neck-Hanging Glasses",0x6F77200E),
    (871640100015,"VisionEyewearAssignRegularChain","Vision & Eyewear - Assign Regular Glasses Chain",0x6F77200F),
    (871640100016,"VisionEyewearAssignReadingChain","Vision & Eyewear - Assign Reading Glasses Chain",0x6F772010),
    (871640100017,"VisionEyewearHangReading","Vision & Eyewear - Hang Reading Glasses (Matching Frames Only)",0x6F772011),
    (871640100018,"VisionEyewearHangRegular","Vision & Eyewear - Hang Regular Glasses (Matching Frames Only)",0x6F772012),
    (871640100019,"VisionEyewearCaptureAlternate1","Vision & Eyewear - Assign Alternate Pair 1",0x6F772013),
    (871640100020,"VisionEyewearCaptureAlternate2","Vision & Eyewear - Assign Alternate Pair 2",0x6F772014),
    (871640100021,"VisionEyewearWearAlternate1","Vision & Eyewear - Wear Alternate Pair 1",0x6F772015),
    (871640100022,"VisionEyewearWearAlternate2","Vision & Eyewear - Wear Alternate Pair 2",0x6F772016),
    (871640100023,"VisionEyewearCyclePairs","Vision & Eyewear - Select Next Saved Pair",0x6F772017),
    (871640100024,"VisionEyewearAssignUniversalChain","Vision & Eyewear - Assign Universal Chain (Worn Necklace)",0x6F772018),
    (871640100025,"VisionEyewearToggleUniversalChain","Vision & Eyewear - Toggle Universal Chain Sharing",0x6F772019),
    (871640100026,"VisionEyewearWearUniversalChain","Vision & Eyewear - Wear Universal Chain Alone",0x6F77201A),
    (871640100027,"VisionEyewearRemoveUniversalChain","Vision & Eyewear - Remove Mod-Equipped Universal Chain",0x6F77201B),
    (871640100028,"VisionEyewearFitRegular","Vision & Eyewear - Cycle Regular Chain Fit",0x6F77201C),
    (871640100029,"VisionEyewearFitReading","Vision & Eyewear - Cycle Reading Chain Fit",0x6F77201D),
    (871640100030,"VisionEyewearFitAlternate1","Vision & Eyewear - Cycle Alternate 1 Chain Fit",0x6F77201E),
    (871640100031,"VisionEyewearFitAlternate2","Vision & Eyewear - Cycle Alternate 2 Chain Fit",0x6F77201F),
    (871640100032,"VisionEyewearCollectionCapture","Glasses Collection - Capture Current Glasses Into Collection",0x6F772020),
    (871640100033,"VisionEyewearCollectionNext","Glasses Collection - Select Next Collected Pair",0x6F772021),
    (871640100034,"VisionEyewearCollectionWear","Glasses Collection - Wear Selected Collected Pair",0x6F772022),
    (871640100035,"VisionEyewearCollectionShow","Glasses Collection - Show Collection Status (eyewear.last)",0x6F772023),
    (871640100036,"VisionEyewearCollectionAssignRegular","Glasses Collection - Assign Selected Pair: Regular (Empty Only)",0x6F772024),
    (871640100037,"VisionEyewearCollectionAssignReading","Glasses Collection - Assign Selected Pair: Readers (Empty Only)",0x6F772025),
    (871640100038,"VisionEyewearCollectionAssignAlternate1","Glasses Collection - Assign Selected Pair: Alternate 1 (Empty Only)",0x6F772026),
    (871640100039,"VisionEyewearCollectionAssignAlternate2","Glasses Collection - Assign Selected Pair: Alternate 2 (Empty Only)",0x6F772027),
    (871640100040,"VisionEyewearCollectionReplaceRegular","Glasses Collection - Replace Regular With Selected Pair",0x6F772028),
    (871640100041,"VisionEyewearCollectionReplaceReading","Glasses Collection - Replace Readers With Selected Pair",0x6F772029),
    (871640100042,"VisionEyewearCollectionReplaceAlternate1","Glasses Collection - Replace Alternate 1 With Selected Pair",0x6F77202A),
    (871640100043,"VisionEyewearCollectionReplaceAlternate2","Glasses Collection - Replace Alternate 2 With Selected Pair",0x6F77202B),
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
