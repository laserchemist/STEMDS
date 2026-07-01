
import json
import os
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
import uuid

# VERSION 1.4 (6/29/2026)

FILE = "student_library.json"

CODE_STRUCTURES = [
    'Please Select',
    'Operation',
    'Function',
    'Method',
    'Index',
    'Other'
]

DATA_TYPES = [
    'integer',
    'float',
    'integer/float',
    'string',
    'list',
    'array',
    'list/array',
    'table',
    'boolean',
    'anything'
]

class LibraryViewer:

    def __init__(self):

        self.active_edit_index = None

        self.data = self.load_library()

        self.create_widgets()

        self.connect_events()

        self.active_edit_mode = None
        self._edit_lock = False

        self.entry_ui_map = {}

        self.out = widgets.Output()

        self.editor_cache = {}

    # ---------------------------------------------
    # DATA
    # ---------------------------------------------

    def load_library(self):

        if not os.path.exists(FILE):
            return []

        try:

            with open(FILE, "r") as f:
                data = json.load(f)

            if isinstance(data, list):
                return data

            return []

        except Exception:
            return []


    def build_main_editor(self, index):

        entry = self.data[index]
    
        w_type = widgets.Dropdown(
            value=entry.get("Structure Type", ""),
            options=CODE_STRUCTURES,
            description="Type:"
        )
    
        w_name = widgets.Text(
            value=entry.get("General Structure", ""),
            description="Structure:"
        )
    
        w_desc = widgets.Textarea(
            value=entry.get("Brief Description", ""),
            description="Description:"
        )
    
        btn_save = widgets.Button(
            description="Save",
            button_style="success"
        )
    
        btn_cancel = widgets.Button(
            description="Cancel",
            button_style="warning"
        )
    
        out = widgets.Output()
    
        def save(_):
            self.data[index]["Structure Type"] = w_type.value
            self.data[index]["General Structure"] = w_name.value
            self.data[index]["Brief Description"] = w_desc.value
            self.save_library()
            self.update_entry_display(index)
        
            ui = self.entry_ui_map[index]
            ui["editor_slot"].layout.display = "none"

            key = (index, "main")
            if key in self.editor_cache:
                del self.editor_cache[key]
    
        def cancel(_):
            ui = self.entry_ui_map[index]
            ui["editor_slot"].layout.display = "none"
    
        btn_save.on_click(save)
        btn_cancel.on_click(cancel)
    
        return widgets.VBox([
            w_type,
            w_name,
            w_desc,
            widgets.HBox([btn_save, btn_cancel]),
            out
        ])

    def build_inputs_editor(self, index):
    
        entry = self.data[index]
    
        rows = []
    
        box = widgets.VBox()
    
        def rebuild():
        
            children = []
        
            for i, (n, r, t) in enumerate(rows):
        
                border = ''
                if i < len(rows) - 1:
                    border = '1px solid #DDD'
        
                btn_delete = widgets.Button(
                    description='',
                    icon='times',
                    button_style='',
                    layout=widgets.Layout(width='80px')
                )
        
                def make_delete_handler(idx):
                    def _delete(_):
                        rows.pop(idx)
                        rebuild()
                    return _delete
        
                btn_delete.on_click(make_delete_handler(i))
        
                children.append(
        
                    widgets.VBox([
                    
                        n,
                        r,
                    
                        widgets.HBox([
                            t,
                            btn_delete
                        ],
                        layout=widgets.Layout(gap='10px', align_items='center'))
                    
                    ],
        
                    layout=widgets.Layout(
                        border_bottom=border,
                        padding='10px 0px 14px 0px',
                        margin='0px 0px 10px 0px'
                    ))
        
                )
        
            box.children = children
    
        for inp in entry.get("Inputs", []):
    
            name = widgets.Text(
                value=inp.get("input", ""),
                description="Input:",
                layout=widgets.Layout(width='95%')
            )
    
            rep = widgets.Textarea(
                value=inp.get("represents", ""),
                description="Represents:",
                layout=widgets.Layout(width='95%', height='70px')
            )
    
            typ = widgets.Dropdown(
                options=DATA_TYPES,
                value=inp.get("type", "anything"),
                description="Type:",
                layout=widgets.Layout(width='220px')
            )
    
            rows.append((name, rep, typ))
    
        rebuild()
    
        def add_row(_):
    
            rows.append((
                widgets.Text(description="Input:"),
                widgets.Textarea(description="Represents:"),
    
                widgets.Dropdown(
                    options=DATA_TYPES,
                    value="anything",
                    description="Type:"
                )
            ))
    
            rebuild()
    
        def save(_):
    
            new_inputs = []
    
            for (n, r, t) in rows:
    
                if not n.value.strip():
                    continue
    
                new_inputs.append({
                    "input": n.value,
                    "represents": r.value,
                    "type": t.value
                })
    
            self.data[index]["Inputs"] = new_inputs
    
            self.save_library()
            self.update_entry_display(index)
        
            ui = self.entry_ui_map[index]
            ui["editor_slot"].layout.display = "none"

            key = (index, "inputs")
            if key in self.editor_cache:
                del self.editor_cache[key]
    
        btn_add = widgets.Button(
            description="Add Input",
            button_style="info"
        )
    
        btn_save = widgets.Button(
            description="Save Inputs",
            button_style="success"
        )
    
        btn_cancel = widgets.Button(
            description="Cancel",
            button_style="warning"
        )
    
        btn_add.on_click(add_row)
        btn_save.on_click(save)
        def cancel(_):
            ui = self.entry_ui_map[index]
            ui["editor_slot"].layout.display = "none"
        
        btn_cancel.on_click(cancel)
    
        return widgets.VBox([
    
            box,
    
            widgets.HBox([
                btn_add,
                btn_save,
                btn_cancel
            ])
    
        ])

    def build_examples_editor(self, index):
    
        entry = self.data[index]
    
        rows = []
    
        box = widgets.VBox()
    
        def rebuild():
    
            children = []
    
            for (c, o, s) in rows:
    
                children.append(
    
                    widgets.VBox([
    
                        widgets.HTML("<b>Code</b>"),
                        c,
    
                        widgets.HTML("<b>Output</b>"),
                        o,
    
                        widgets.HTML("<b>Source</b>"),
                        s
    
                    ])
    
                )
    
            box.children = children
    
        for ex in entry.get("Examples", []):
    
            code = widgets.Textarea(
                value=ex.get("code", "")
            )
    
            output = widgets.Textarea(
                value=ex.get("output", "")
            )
    
            source = widgets.Text(
                value=ex.get("source", "")
            )
    
            rows.append((code, output, source))
    
        rebuild()
    
        def add_row(_):
    
            rows.append((
                widgets.Textarea(),
                widgets.Textarea(),
                widgets.Text()
            ))
    
            rebuild()
    
        def save(_):
    
            new_examples = []
    
            for (c, o, s) in rows:
    
                if not c.value.strip():
                    continue
    
                new_examples.append({
                    "code": c.value,
                    "output": o.value,
                    "source": s.value
                })
    
            self.data[index]["Examples"] = new_examples
    
            self.save_library()
            self.update_entry_display(index)
        
            ui = self.entry_ui_map[index]
            ui["editor_slot"].layout.display = "none"

            key = (index, "examples")
            if key in self.editor_cache:
                del self.editor_cache[key]
    
        btn_add = widgets.Button(
            description="Add Example",
            button_style="info"
        )
    
        btn_save = widgets.Button(
            description="Save Examples",
            button_style="success"
        )
    
        btn_cancel = widgets.Button(
            description="Cancel",
            button_style="warning"
        )
    
        btn_add.on_click(add_row)
        btn_save.on_click(save)
        def cancel(_):
            ui = self.entry_ui_map[index]
            ui["editor_slot"].layout.display = "none"
        
        btn_cancel.on_click(cancel)
    
        return widgets.VBox([
    
            box,
    
            widgets.HBox([
                btn_add,
                btn_save,
                btn_cancel
            ])
    
        ])
    # ---------------------------------------------
    # WIDGETS
    # ---------------------------------------------

    def create_widgets(self):

        self.w_search = widgets.Text(
            description='Search:',
            placeholder='Search structures, descriptions, libraries...',
            layout=widgets.Layout(width='500px'),
            style={'description_width': '90px'}
        )

        self.w_type = widgets.Dropdown(
            description='Type:',
            options=['All'] + sorted(list({
                e.get('Structure Type', 'Other')
                for e in self.data
            })),
            value='All',
            layout=widgets.Layout(width='300px'),
            style={'description_width': '90px'}
        )

        self.w_library = widgets.Dropdown(
            description='Library:',
            options=['All'] + sorted(list({
                e.get('Library', '') or 'Python Default'
                for e in self.data
            })),
            value='All',
            layout=widgets.Layout(width='300px'),
            style={'description_width': '90px'}
        )

        self.w_sort = widgets.Dropdown(
            description='Sort:',
            options=[
                'Alphabetical',
                'Number of Arguments',
                'Source'
            ],
            value='Alphabetical',
            layout=widgets.Layout(width='300px'),
            style={'description_width': '90px'}
        )

    # ---------------------------------------------
    # EVENTS
    # ---------------------------------------------

    def connect_events(self):

        self.w_search.observe(self.on_change, names='value')
        self.w_type.observe(self.on_change, names='value')
        self.w_library.observe(self.on_change, names='value')

        self.w_sort.observe(
            self.on_change,
            names='value'
        )

    def on_change(self, change):

        self.refresh_results()

    # ---------------------------------------------
    # FILTERING
    # ---------------------------------------------

    def matches_search(self, entry, query):

        if not query:
            return True

        query = query.lower()

        searchable_text = " ".join([
            str(entry.get('General Structure', '')),
            str(entry.get('Brief Description', '')),
            str(entry.get('Additional Details', '')),
            str(entry.get('Examples', '')),
            str(entry.get('Library', '')),
            str(entry.get('Source', ''))
        ]).lower()

        return query in searchable_text

    def filter_entries(self):

        results = []

        for index, entry in enumerate(self.data):

            # SEARCH
            if not self.matches_search(
                entry,
                self.w_search.value.strip()
            ):
                continue

            # TYPE
            if (
                self.w_type.value != 'All'
                and
                entry.get('Structure Type') != self.w_type.value
            ):
                continue

            # LIBRARY
            library_value = (
                entry.get('Library')
                or
                'Python Default'
            )

            if (
                self.w_library.value != 'All'
                and
                library_value != self.w_library.value
            ):
                continue

            results.append((index, entry))

        # -----------------------------------------
        # SORTING
        # -----------------------------------------
        
        if self.w_sort.value == 'Alphabetical':
        
            results.sort(
                key=lambda x:
                x[1].get(
                    'General Structure',
                    ''
                ).lower()
            )
        
        elif self.w_sort.value == 'Number of Arguments':
        
            def parse_args(entry):
        
                raw = entry.get(
                    'Number of Arguments',
                    ''
                )
        
                try:
                    return int(raw)
        
                except:
                    return 999999
        
            results.sort(
                key=lambda x:
                parse_args(x[1])
            )
        
        elif self.w_sort.value == 'Source':
        
            results.sort(
                key=lambda x:
                x[1].get(
                    'Source',
                    ''
                ).lower()
            )

        return results

    # ---------------------------------------------
    # DISPLAY
    # ---------------------------------------------

    def update_entry_display(self, index):
    
        ui = self.entry_ui_map.get(index)
    
        if not ui:
            return
    
        entry = self.data[index]
    
        ui["header_html"].value = f"""
        <div style="
            font-size:20px;
            font-weight:700;
            color:#9E1B34;
            padding:8px;
        ">
            {entry.get('General Structure', '')}
        </div>
    
        <div style="
            padding-left:8px;
            color:#666;
            margin-bottom:8px;
        ">
            {entry.get('Structure Type', '')}
            |
            {entry.get('Library', '') or 'Python Default'}
        </div>
        """
    
        ui["detail_html"].value = self.build_details_html(entry)
        ui["editor_slot"].layout.display = "none"

    def build_details_html(self, entry):

            
        inputs_html = ""
    
        for inp in entry.get('Inputs', []):
        
            inputs_html += f"""
            <div style='margin-left:20px;margin-top:8px;'>
        
                <b>{inp.get('input', '')}</b>
                → {inp.get('represents', '')}
        
                <br>
        
                <span style='color:#666;'>
                    Type: {inp.get('type', '')}
                </span>
        
            </div>
            """

        examples_html = ""
        for ex in entry.get("Examples", []):
        
            examples_html += f"""
            <div style='margin-top:14px;padding:10px;border:1px solid #DDD;border-radius:8px;'>
        
                <div>
                    <b>Code:</b>
                    <pre style="
                        background:#F7F7F7;
                        padding:10px;
                        border-radius:6px;
                        overflow-x:auto;">
                    {ex.get('code', '')}</pre>
                </div>
        
                <div>
                    <b>Output:</b>
                    <pre style="
                        background:#F7F7F7;
                        padding:10px;
                        border-radius:6px;
                        overflow-x:auto;">
                    {ex.get('output', '')}</pre>
                </div>
        
                <div style='color:#666;'>
                    Found in:
                    {ex.get('source', '')}
                </div>
        
            </div>
            """

        return f"""
        <div style="
            border-top:1px solid #DDD;
            margin-top:10px;
            padding-top:12px;
        ">
    
            <div><b>Description:</b>
            {entry.get('Brief Description', '')}</div>
    
            <div style='margin-top:8px;'>
            <b>Additional Details:</b>
            {entry.get('Additional Details', '')}
            </div>
    
            <div style='margin-top:8px;'>
            <b>Source:</b>
            {entry.get('Source', '')}
            </div>
    
            <div style='margin-top:12px;'>
            <b>Inputs:</b>
            {inputs_html}
            </div>

            <div style='margin-top:12px;'>
            <b>Examples:</b>
            {examples_html}
            </div>
    
        </div>
        """

    def display_entry(self, entry, index):
    
        # -----------------------------------------
        # HEADER
        # -----------------------------------------
    
        header_html = widgets.HTML(f"""
        <div style="
            font-size:20px;
            font-weight:700;
            color:#9E1B34;
            padding:8px;
        ">
            {entry.get('General Structure', '')}
        </div>
    
        <div style="
            padding-left:8px;
            color:#666;
            margin-bottom:8px;
        ">
            {entry.get('Structure Type', '')}
            |
            {entry.get('Library', '') or 'Python Default'}
        </div>
        """)
    
        # -----------------------------------------
        # FULL DETAILS
        # -----------------------------------------


        details = widgets.HTML(
            self.build_details_html(entry)
        )
    
        # -----------------------------------------
        # COLLAPSIBLE AREA
        # -----------------------------------------
    
        detail_box = widgets.VBox([details])
        detail_box.layout.display = "none"
    
        # -----------------------------------------
        # TOGGLE BUTTON
        # -----------------------------------------
    
        btn_toggle = widgets.Button(
            description='Expand',
            button_style='info',
            icon='chevron-down',
            layout=widgets.Layout(width='95px')
        )
        
        def toggle(_):
            if detail_box.layout.display == "none":
                detail_box.layout.display = "block"
                btn_toggle.description = "Collapse"
                btn_toggle.icon = "chevron-up"
            else:
                detail_box.layout.display = "none"
                btn_toggle.description = "Expand"
                btn_toggle.icon = "chevron-down"
        
        btn_toggle.on_click(toggle)
        
        edit_menu = widgets.Dropdown(
            options=[
                ('Edit...', ''),
                ('Main Info', 'main'),
                ('Inputs', 'inputs'),
                ('Examples', 'examples')
            ],
            value='',
            layout=widgets.Layout(width='150px')
        )
        
        def handle_edit(change):
            if change['name'] != 'value':
                return
        
            choice = change['new']
            if choice:
                self.open_editor(choice, index)
        
            edit_menu.value = ''
        
        edit_menu.observe(handle_edit, names='value')
        
        btn_delete = widgets.Button(
            description='Delete',
            button_style='danger',
            icon='trash',
            layout=widgets.Layout(width='90px')
        )
        
        btn_delete.on_click(lambda b, i=index: self.delete_entry(i))
        
        buttons = widgets.HBox([
            btn_toggle,
            edit_menu,
            btn_delete
        ])
    
        # -----------------------------------------
        # FINAL CARD
        # -----------------------------------------

        editor_slot = widgets.VBox([])
        editor_slot.layout.display = "none"
    
        card = widgets.VBox([
            header_html,
            buttons,
            detail_box,
            editor_slot
        ])
    
        card.layout = widgets.Layout(
            border='2px solid #9E1B34',
            padding='16px',
            margin='8px',
            border_radius='12px'
        )
    
        return {
            "card": card,
            "editor_slot": editor_slot,
            "header_html": header_html,
            "detail_html": details,
            "detail_box": detail_box
        }

    def refresh_results(self):

        with self.out:

            self.out.clear_output(wait=True)

            results = self.filter_entries()

            display(HTML(f"""
            <div style='margin-top:10px;margin-bottom:10px;'>
                <b>{len(results)}</b> entries found.
            </div>
            """))

            if not results:

                display(HTML(
                    """
                    <div style='color:#999;'>
                        No matching entries found.
                    </div>
                    """
                ))

                return

            cards = []

            self.entry_ui_map = {}
            
            for index, entry in results:
                ui = self.display_entry(entry, index)
            
                entry_id = index
            
                cards.append(ui["card"])
                self.entry_ui_map[entry_id] = ui
            
            grid = widgets.GridBox(
                cards,
                layout=widgets.Layout(
                    grid_template_columns='repeat(2, 1fr)',
                    grid_gap='20px',
                    width='100%'
                )
            )
            
            display(grid)

    # ---------------------------------------------
    # MAIN DISPLAY
    # ---------------------------------------------

    def hide_all_editors(self):

        for ui in self.entry_ui_map.values():
    
            slot = ui["editor_slot"]
            slot.layout.display = "none"
    
        self.active_edit_index = None
        self.active_edit_mode = None
    
    def display(self):
    
        title = widgets.HTML("""
        <div style='font-size:28px;font-weight:700;color:#9E1B34;margin-bottom:14px;'>
            Student Library Viewer
        </div>
        """)
    
        controls = widgets.HBox([
            self.w_search,
            self.w_type,
            self.w_library,
            self.w_sort
        ])
    
        app = widgets.VBox([
            title,
            controls,
            self.out
        ])
    
        display(app)
    
        self.refresh_results()

    def open_editor(self, mode, index):
    
        self.hide_all_editors()
    
        ui = self.entry_ui_map[index]
        slot = ui["editor_slot"]
    
        key = (index, mode)
    
        if key not in self.editor_cache:
    
            if mode == "main":
                editor = self.build_main_editor(index)
    
            elif mode == "inputs":
                editor = self.build_inputs_editor(index)
    
            elif mode == "examples":
                editor = self.build_examples_editor(index)
    
            self.editor_cache[key] = editor
    
        slot.children = [self.editor_cache[key]]
        slot.layout.display = "block"

    def save_library(self):

        with open(FILE, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def delete_entry(self, index):
    
        del self.data[index]
    
        self.save_library()
        self.refresh_results()