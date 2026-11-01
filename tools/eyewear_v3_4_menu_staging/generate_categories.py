"""Generate v3.4 Realistic Glasses pie menu category tuning and a SimData
XML *authoring specification*. A valid game binary SimData must be exported with
Tdesc Builder/Sims 4 Studio and verified BEFORE these categories are shipped.
Do NOT bundle only these XML files as a playable package.
"""
import json
from pathlib import Path
from xml.etree import ElementTree as ET

SRC = Path("tools/eyewear_v3_3/build_package.py")
OUT = Path("build/eyewear_v3_4_menu_staging")
OUT.mkdir(parents=True, exist_ok=True)

# Stable 64-bit category instance identifiers reserved for the mod.
ROOT = 871640200000
CATEGORY_NAMES = [
    ("root", "Realistic Glasses", None),
    ("collection", "My Glasses Collection", "root"),
    ("wear", "Wear or Remove Glasses", "root"),
    ("chains", "Glasses Chains", "root"),
    ("fitting", "Chain Fit", "chains"),
    ("sports", "Sports and Cheerleading", "root"),
    ("preferences", "Vision and Preferences", "root"),
]
CATEGORY_IDS = {key: ROOT + i for i, (key, _, _) in enumerate(CATEGORY_NAMES)}
CATEGORY_KEYS = {key: 0x6F773000 + i for i, (key, _, _) in enumerate(CATEGORY_NAMES)}

# The existing v3.3 build generator has the authoritative class/tuning IDs.
import ast
tree = ast.parse(SRC.read_text(encoding="utf-8"))
entries = next(ast.literal_eval(node.value) for node in tree.body
               if isinstance(node, ast.Assign) and
               any(isinstance(t, ast.Name) and t.id == "ENTRIES" for t in node.targets))
BY_CLASS = {cls: (instance, label, key) for instance, cls, label, key in entries}
assignments = {
    "collection": [
        "CollectionCapture", "CollectionNext", "CollectionWear", "CollectionShow",
        "CollectionAssignRegular", "CollectionAssignReading",
        "CollectionAssignAlternate1", "CollectionAssignAlternate2",
        "CollectionReplaceRegular", "CollectionReplaceReading",
        "CollectionReplaceAlternate1", "CollectionReplaceAlternate2",
        "Remember", "RememberReading", "CaptureAlternate1", "CaptureAlternate2",
    ],
    "wear": ["Remove", "PutOn", "PutOnReading", "WearAlternate1", "WearAlternate2", "CyclePairs"],
    "chains": [
        "RememberChain", "ChainAssignRegular", "ChainAssignReading",
        "ChainAssignAlternate1", "ChainAssignAlternate2", "ChainApplySelected",
        "ChainRemoveSelected", "ChainBehaviorCycle", "AssignUniversalChain",
        "ToggleUniversalChain", "WearUniversalChain", "RemoveUniversalChain",
        "AssignNeck", "AssignRegularChain", "AssignReadingChain",
        "HangNeck", "HangReading", "HangRegular", "FaceAndNeck",
        "PutOnFromNeck", "RemoveNeck",
    ],
    "fitting": ["FitRegular", "FitReading", "FitAlternate1", "FitAlternate2"],
    "sports": ["MarkSports", "MarkCheer"],
    "preferences": ["UseRegularForReading", "StoreInInventory"],
}
mapping = {}
for category, suffixes in assignments.items():
    for suffix in suffixes:
        cls = "VisionEyewear" + suffix
        if cls not in BY_CLASS:
            raise ValueError("Unknown interaction class " + cls)
        if cls in mapping:
            raise ValueError("Duplicate interaction " + cls)
        mapping[cls] = category
missing = sorted(set(BY_CLASS) - set(mapping))
if missing:
    raise ValueError("Uncategorized interactions: " + ", ".join(missing))

for key, label, parent in CATEGORY_NAMES:
    name = "WPS_PieMenu_RealisticGlasses_" + key
    cat = ET.Element("I", {"c": "PieMenuCategory", "i": "pie_menu_category",
                           "m": "interactions.pie_menu_category",
                           "n": name, "s": str(CATEGORY_IDS[key])})
    ET.SubElement(cat, "T", {"n": "_collapsible"}).text = "False"
    ET.SubElement(cat, "T", {"n": "_display_name"}).text = "0x{:08X}".format(CATEGORY_KEYS[key])
    ET.SubElement(cat, "T", {"n": "_display_priority"}).text = "5"
    if parent:
        ET.SubElement(cat, "T", {"n": "_parent"}).text = str(CATEGORY_IDS[parent])
    (OUT / (name + ".xml")).write_bytes(
        b'<?xml version="1.0" encoding="UTF-8"?>\n' +
        ET.tostring(cat, encoding="utf-8"))

# Authoring XML for a human/tool to import and export as *binary* SimData.
# Keep schema and fields in sync with the tuning before using the game.
for key, label, parent in CATEGORY_NAMES:
    name = "WPS_PieMenu_RealisticGlasses_" + key
    simdata = ET.Element("SimData", {"version": "0x00000101", "u": "0x00000000"})
    inst = ET.SubElement(ET.SubElement(simdata, "Instances"), "I", {
        "name": name, "schema": "PieMenuCategory", "type": "Object"})
    for field, val in [
        ("_collapsible", "0"), ("_display_name", "0x{:08X}".format(CATEGORY_KEYS[key])),
        ("_display_priority", "5"), ("_icon", "00000000-00000000-0000000000000000"),
        ("_parent", str(CATEGORY_IDS[parent]) if parent else "0"),
        ("_special_category", "0")
    ]:
        ET.SubElement(inst, "T", {"name": field}).text = val
    ET.SubElement(inst, "L", {"name": "mood_overrides"})
    schema = ET.SubElement(ET.SubElement(simdata, "Schemas"),
                           "Schema", {"name": "PieMenuCategory", "schema_hash": "0x022065C1"})
    columns = ET.SubElement(schema, "Columns")
    for field, typ in [
        ("_collapsible", "Boolean"), ("_display_name", "LocalizationKey"),
        ("_display_priority", "Int32"), ("_icon", "ResourceKey"),
        ("_parent", "TableSetReference"), ("_special_category", "Int64"),
        ("mood_overrides", "Vector")
    ]:
        ET.SubElement(columns, "Column", {"name": field, "type": typ,
                                          "flags": "0x00000000"})
    (OUT / (name + ".simdata.xml")).write_bytes(
        b'<?xml version="1.0" encoding="UTF-8"?>\n' +
        ET.tostring(simdata, encoding="utf-8"))

# The authoritative interaction category and cleaned-up label mapping.
data = {
    "categories": [
        {"key": key, "name": label, "instance": CATEGORY_IDS[key],
         "parent": parent, "string_key": "0x{:08X}".format(CATEGORY_KEYS[key])}
        for key, label, parent in CATEGORY_NAMES
    ],
    "interactions": [
        {"class": cls, "instance": BY_CLASS[cls][0],
         "category": category, "category_instance": CATEGORY_IDS[category],
         "original_label": BY_CLASS[cls][1],
         "menu_label": BY_CLASS[cls][1].replace("Vision & Eyewear - ", "").replace("Glasses Collection - ", "").replace("Chain Controls - ", "")}
        for cls, category in mapping.items()
    ],
}
(OUT / "menu_mapping.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
print("Staged {} menu categories and {} actions (not a shippable package).".format(
    len(CATEGORY_NAMES), len(mapping)))
