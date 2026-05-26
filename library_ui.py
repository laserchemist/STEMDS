import ipywidgets as widgets
from IPython.display import display, HTML
import numpy as np

# VERSION 1.3 (5/26/2026)

class LibraryUI:

    def __init__(self):
        self.inputs_widgets = []

        self.style_lbl = {
            'description_width': '160px'
        }

        self.CODE_STRUCTURES = [
            'Please Select',
            'Operation',
            'Function',
            'Method',
            'Index',
            'Other'
        ]

        self.MAX_INPUTS = 6

        self.MAX_EXAMPLES = 4

        self.DATA_TYPES = [
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

        self.ALPHABET = [
            'a', 'b', 'c', 'd', 'e', 'f'
        ]

        self.SAMPLE_ROLES = [
            'a column header',
            'a string containing (another input)',
            'a function name',
            'a math expression'
        ]

        self.STATUS = [
            'Required',
            'Optional'
        ]

        self.create_identity_widgets()
        self.create_input_widgets()
        self.create_example_widgets()
        self.create_buttons()

    # ---------------------------------------------
    # IDENTITY WIDGETS
    # ---------------------------------------------

    def create_identity_widgets(self):

        self.w_struc = widgets.Dropdown(
            description='Structure Type:',
            options=self.CODE_STRUCTURES,
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

        self.w_name = widgets.Text(
            description='General Structure:',
            placeholder='e.g. print(a, b)',
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

        self.w_library = widgets.Text(
            description='Library:',
            placeholder='e.g. numpy, datascience, etc.',
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

        self.w_num_inputs = widgets.Text(
            description='Number of Arguments:',
            placeholder='e.g. 4 (if unlimited, enter -1)',
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

        self.w_description = widgets.Textarea(
            description='Brief Description:',
            placeholder='e.g. puts arguments to output',
            style=self.style_lbl,
            layout=widgets.Layout(
                width='600px',
                height='90px'
            )
        )

        self.w_additional = widgets.Textarea(
            description='Any additional details:',
            placeholder='Optional notes...',
            style=self.style_lbl,
            layout=widgets.Layout(
                width='600px',
                height='110px'
            )
        )

        self.w_source = widgets.Text(
            description='Where did you learn this:',
            placeholder='e.g. Lab 2, Question 4',
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

    def create_example_widgets(self):
    
        self.examples_widgets = []

        self.examples_grid = widgets.GridBox(
            children=[],
            layout=widgets.Layout(
                grid_template_columns="repeat(auto-fit, minmax(420px, 1fr))",
                grid_gap="12px",
                width="99%",
                max_width="99%"
            )
        )
        
        self.btn_add_example = widgets.Button(
            description="Add Example",
            button_style="info",
            icon="plus"
        )
        
        self.btn_add_example.on_click(self.add_example_row)


    def add_example_row(self, _):
    
        code_w = widgets.Textarea(
            description='Code:',
            placeholder="e.g. print('Hello World')",
            style={'description_width': '70px'},
            layout=widgets.Layout(width='99%', height='90px')
        )
    
        output_w = widgets.Textarea(
            description='Output:',
            placeholder="e.g. 'Hello World' (If it's a big and complicated output (like a table), you can also describe it instead.",
            style={'description_width': '70px'},
            layout=widgets.Layout(width='99%', height='90px')
        )
    
        source_w = widgets.Text(
            description='Source:',
            placeholder="e.g. Lab 3 Question 5",
            style={'description_width': '70px'},
            layout=widgets.Layout(width='99%')
        )
    
        # small "x" delete button (top-right style)
        btn_delete = widgets.Button(
            description="",
            icon="times",
            button_style="",
            layout=widgets.Layout(
                width="28px",
                height="28px",
                padding="0px"
            ),
            tooltip="Delete example"
        )
    
        # container for layout control
        header = widgets.HBox([widgets.Label(""), btn_delete])
        header.layout.justify_content = "flex-end"
    
        body = widgets.VBox([code_w, output_w, source_w])
    
        card = widgets.VBox([header, body])
    
        card.layout = widgets.Layout(
            border="1px solid #DDD",
            padding="10px",
            margin="5px",
            border_radius="10px",
            width="99%",
            max_width="520px"
        )
    
        entry = {
            "card": card,
            "widgets": (code_w, output_w, source_w)
        }
    
        self.examples_widgets.append(entry)
    
        def delete_row(_btn, entry=entry):
            # remove safely
            if entry in self.examples_widgets:
                self.examples_widgets.remove(entry)
    
            # single source of truth rebuild (IMPORTANT)
            self.examples_grid.children = tuple(
                e["card"] for e in self.examples_widgets
            )
    
        btn_delete.on_click(delete_row)
    
        # IMPORTANT: only rebuild from list — do NOT append manually
        self.examples_grid.children = tuple(
            e["card"] for e in self.examples_widgets
        )

    # ---------------------------------------------
    # INPUT WIDGETS
    # ---------------------------------------------

    def create_input_widgets(self):

        self.inputs_widgets = []
    
        self.inputs_grid = widgets.GridBox(
            children=[],
            layout=widgets.Layout(
                grid_template_columns="repeat(auto-fit, minmax(420px, 1fr))",
                grid_gap="12px",
                width="99%",
                max_width="99%"
            )
        )
    
        self.btn_add_input = widgets.Button(
            description="Add Input",
            button_style="info",
            icon="plus"
        )
    
        self.btn_add_input.on_click(self.add_input_row)

    def add_input_row(self, _):
    
        identifier_w = widgets.Text(
            description="Input:",
            placeholder="e.g. a",
            layout=widgets.Layout(width='95%')
        )
    
        role_w = widgets.Textarea(
            description="Represents:",
            placeholder="meaning / role",
            layout=widgets.Layout(width='95%', height='70px')
        )
    
        type_w = widgets.Dropdown(
            description="Type:",
            options=['---'] + self.DATA_TYPES,
            layout=widgets.Layout(width='220px')
        )
    
        status_w = widgets.Dropdown(
            description="Status:",
            options=['---'] + self.STATUS,
            layout=widgets.Layout(width='220px')
        )
    
        assume_w = widgets.Text(
            description="Assumed:",
            placeholder="optional default",
            layout=widgets.Layout(width='220px')
        )
    
        btn_delete = widgets.Button(
            description="",
            icon="times",
            button_style="",
            layout=widgets.Layout(width="32px", height="32px")
        )
    
        header = widgets.HBox([widgets.Label(""), btn_delete])
        header.layout.justify_content = "flex-end"
    
        body = widgets.VBox([
            identifier_w,
            role_w,
            widgets.VBox([
                widgets.HBox([type_w, status_w]),
                assume_w
            ])
        ])
    
        card = widgets.VBox([header, body])
    
        card.layout = widgets.Layout(
            border="1px solid #DDD",
            padding="10px",
            margin="5px",
            border_radius="10px",
            width="99%",
            max_width="520px"
        )
    
        entry = {
            "card": card,
            "widgets": {
                "input": identifier_w,
                "represents": role_w,
                "type": type_w,
                "status": status_w,
                "assumed": assume_w
            }
        }
    
        self.inputs_widgets.append(entry)
    
        def delete(_btn, entry=entry):
            if entry in self.inputs_widgets:
                self.inputs_widgets.remove(entry)
    
            self.inputs_grid.children = tuple(e["card"] for e in self.inputs_widgets)
    
        btn_delete.on_click(delete)
    
        self.inputs_grid.children = tuple(e["card"] for e in self.inputs_widgets)

    def collect_inputs(self):

        result = []
    
        for entry in self.inputs_widgets:
    
            w = entry["widgets"]
    
            inp = w["input"].value.strip()
    
            if not inp:
                continue
    
            result.append({
                "input": inp,
                "represents": w["represents"].value,
                "type": w["type"].value,
                "status": w["status"].value,
                "assumed": w["assumed"].value
            })
    
        return result

    def clear_inputs(self):
        self.inputs_widgets = []
        self.inputs_grid.children = ()
    # ---------------------------------------------
    # BUTTONS / OUTPUTS
    # ---------------------------------------------

    def create_buttons(self):

        self.btn_submit = widgets.Button(
            description="Submit Entry",
            button_style='danger',
            icon='plus'
        )

        self.out_submit = widgets.Output()

    # ---------------------------------------------
    # DISPLAY
    # ---------------------------------------------

    def display_interface(self):

        display(
            widgets.HTML(
                '''
                <div style="
                    font-size:20px;
                    font-weight:600;
                    color:#9E1B34;
                    margin-bottom:6px;
                ">
                    Add a new entry to your library:
                </div>
                '''
            )
        )

        display(
            self.w_struc,
            self.w_name,
            self.w_library,
            self.w_num_inputs,
            self.w_description,
            self.w_additional,
            self.w_source
        )

        display(
            widgets.HTML(
                '''
                <div style="
                    font-size:20px;
                    font-weight:600;
                    color:#9E1B34;
                    margin-bottom:6px;
                    margin-top:15px;
                ">
                    What does each input represent?
                </div>
                '''
            )
        )

        display(self.inputs_grid)
        display(self.btn_add_input)

        display(
            widgets.HTML('<div style="font-size:20px;font-weight:600;color:#9E1B34;margin-top:10px;">Guide:</div>'
        ))
        display(widgets.HTML(
            '<div style="color:#888;font-size:15px;margin-top:3px;">Leave unused input rows blank; If entering a method, make the first row the Object.</div>'
        ))
        display(widgets.HTML(
            '<div style="color:#888;font-size:15px;margin-top:3px;"><b>Input:</b> The same name you gave this input in the general structure.</div>'
        ))
        display(widgets.HTML(
            '<div style="color:#888;font-size:15px;margin-top:3px;"><b>Represents:</b> Oftentimes, inputs will not just be any old string or list, but something that has a relationship with the other inputs or is of a certain quality.</div>'
        ))
        display(widgets.HTML(
            '<div style="color:#888;font-size:15px;margin-top:3px;"><b>Type:</b> The datatype. If this is more complex (e.g. a list <i>of strings</i>), indicate as such in the Represents box.</div>'
        ))
        display(widgets.HTML(
            '<div style="color:#888;font-size:15px;margin-top:3px;"><b>Status:</b> Is the input required, or can you omit it? (only about 5 or so things in this whole course have omissable inputs that actually matter and will be used often; you do not have to scour the dictionary to find all known omissable inputs for a given function/method.)</div>'
        ))
        display(widgets.HTML(
            '<div style="color:#888;font-size:15px;margin-top:3px;"><b>Assumed:</b> Only fill this out if the input in question is omissable. An example of an omissible argument is the start and step of np.arange, which, when omitted, are assumed to be 0 and 1 respectively. (You will learn this in Lab 2.)</div>'
        ))

        display(
            widgets.HTML(
                """
                <div style="
                    font-size:20px;
                    font-weight:600;
                    color:#9E1B34;
                    margin-top:20px;
                    margin-bottom:10px;
                ">
                    Example Usage
                </div>
                """
            )
        )
        
        display(self.examples_grid)
        display(self.btn_add_example)

        display(
            self.btn_submit,
            self.out_submit
        )

    # ---------------------------------------------
    # MESSAGES
    # ---------------------------------------------

    def show_errors(self, errors):

        with self.out_submit:

            self.out_submit.clear_output()

            display(HTML(
                "<br>".join(
                    f'<div style="color:#9E1B34;font-weight:bold;">⚠️ {e}</div>'
                    for e in errors
                )
            ))

    def show_success(self, entry):

        with self.out_submit:

            self.out_submit.clear_output()

            entry["Inputs"] = self.collect_inputs()

            display(HTML(f"""
            <div style="
                background:#F5F2EC;
                border:2px solid #9E1B34;
                border-radius:12px;
                padding:20px;
                max-width:650px;
                font-family:system-ui;
            ">

                <div style="
                    font-size:22px;
                    font-weight:700;
                    color:#9E1B34;
                    margin-bottom:10px;
                ">
                    ✅ Entry Added
                </div>

                <div>
                    <b>General Structure:</b>
                    {entry["General Structure"]}
                </div>

                <div>
                    <b>Structure Type:</b>
                    {entry["Structure Type"]}
                </div>

                <div>
                    <b>Description:</b>
                    {entry["Brief Description"]}
                </div>

            </div>
            """))