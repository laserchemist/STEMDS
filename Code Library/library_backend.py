import json
import os
import time
import tempfile

FILE = "student_library.json"

# VERSION 1.5 (7/2/2026)

# ---------------------------------------------
# FILE MANAGEMENT
# ---------------------------------------------

def initialize_library():
    """
    Ensures the JSON file exists and is valid.
    """

    if not os.path.exists(FILE):

        with open(FILE, "w") as f:
            json.dump([], f, indent=2)

        return

    try:
        with open(FILE, "r") as f:
            data = json.load(f)

        if not isinstance(data, list):

            with open(FILE, "w") as f:
                json.dump([], f, indent=2)

    except json.JSONDecodeError:

        with open(FILE, "w") as f:
            json.dump([], f, indent=2)


def load_library():

    try:
        with open(FILE, "r") as f:

            data = json.load(f)

            if isinstance(data, list):
                return data

            return []

    except (FileNotFoundError, json.JSONDecodeError):

        return []


def save_library(data):

    os.makedirs(os.path.dirname(FILE) or ".", exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        dir=os.path.dirname(FILE) or ".",
        suffix=".tmp"
    ) as tmp:

        json.dump(data, tmp, indent=2)

        temp_name = tmp.name

    os.replace(temp_name, FILE)


# ---------------------------------------------
# INPUT COLLECTION
# ---------------------------------------------

def collect_inputs(inputs_widgets):
    collected = []

    for entry in inputs_widgets:

        w = entry["widgets"]

        identifier = w["input"].value.strip()
        if not identifier:
            continue

        collected.append({
            "input": identifier,
            "represents": w["represents"].value,
            "type": w["type"].value
        })

    return collected

def collect_examples(examples_widgets):

    collected = []

    for (
        code_w,
        output_w,
        source_w
    ) in examples_widgets:

        code = code_w.value.strip()

        if not code:
            continue

        collected.append({

            "code":
                code,

            "output":
                output_w.value.strip(),

            "source":
                source_w.value.strip()

        })

    return collected

# ---------------------------------------------
# VALIDATION
# ---------------------------------------------

def validate_form(ui):

    errors = []

    if ui.w_struc.value == ui.CODE_STRUCTURES[0]:
        errors.append("Please select a Structure Type.")

    if not ui.w_name.value.strip():
        errors.append("General Structure is required.")

    if not ui.w_description.value.strip():
        errors.append("Brief Description is required.")

    if not ui.collect_inputs():
        errors.append("At least one input is required.")

    return errors


# ---------------------------------------------
# ENTRY CREATION
# ---------------------------------------------

def build_entry(ui):

    return {

        "Structure Type":
            ui.w_struc.value,

        "General Structure":
            ui.w_name.value.strip(),

        "Library":
            ui.w_library.value.strip(),

        "Number of Arguments":
            ui.w_num_inputs.value.strip(),

        "Brief Description":
            ui.w_description.value.strip(),

        "Additional Details":
            ui.w_additional.value.strip(),

        "Source":
            ui.w_source.value.strip(),

        "Inputs":
            collect_inputs(ui.inputs_widgets),

        "Timestamp":
            time.strftime("%Y-%m-%d %H:%M:%S")
    }


def replace_existing(entries, new_entry):

    name = new_entry["General Structure"].lower()

    filtered = [

        e for e in entries

        if e.get(
            "General Structure",
            ""
        ).lower() != name
    ]

    filtered.append(new_entry)

    return filtered

def handle_submit(ui, _):

    errors = validate_form(ui)

    if errors:
        ui.show_errors(errors)
        return

    entry = build_entry(ui)

    library = load_library()

    library = replace_existing(library, entry)

    save_library(library)

    ui.show_success(entry)