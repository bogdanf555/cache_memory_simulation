import PySimpleGUI as sg

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 700

config_panel_column = [
    [sg.Text("Cache Configuration")],
    [sg.Text("Capacity (B): "), sg.In(size=(15, 1), key="-CACHE_CAPACITY-")],
    [sg.Text("Associativity: "), sg.In(size=(15, 1), key="-ASSOCIATIVITY-")],
    [sg.Text("Block size (B): "), sg.In(size=(15, 1), key="-BLOCK_SIZE-")],
    [sg.Text("Ram Configuration")],
    [sg.Text("Capacity (MB): "), sg.In(size=(15, 1), key="-RAM_CAPACITY-")],
    [sg.Button("Create"), sg.Button("Start")],
]

layout = [
    [
        sg.Column(config_panel_column, size=(300, WINDOW_WIDTH), pad=(50, 50)),
        sg.VSeperator(),
        sg.Column([[]], key="-COLUMN_TABLE-"),
    ]
]


class UserInterface:
    def __init__(self):
        self.title = "Cache Simulation"
        self.window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.layout = layout

        self.window = sg.Window(self.title, self.layout, size=self.window_size)

    def create_table(self, headings, values):
        print(values)
        table = sg.Table(
            values=values,
            headings=headings,
            # max_col_width=25,
            auto_size_columns=True,
            justification="right",
            key="-TABLE-",
            row_height=25,
            num_rows=len(values),
        )

        new_layout = [
            [
                sg.Column(
                    [
                        [sg.Text("Cache Configuration")],
                        [
                            sg.Text("Capacity (B): "),
                            sg.In(size=(15, 1), key="-CACHE_CAPACITY-"),
                        ],
                        [
                            sg.Text("Associativity: "),
                            sg.In(size=(15, 1), key="-ASSOCIATIVITY-"),
                        ],
                        [
                            sg.Text("Block size (B): "),
                            sg.In(size=(15, 1), key="-BLOCK_SIZE-"),
                        ],
                        [sg.Text("Ram Configuration")],
                        [
                            sg.Text("Capacity (MB): "),
                            sg.In(size=(15, 1), key="-RAM_CAPACITY-"),
                        ],
                        [sg.Button("Create"), sg.Button("Start")],
                    ],
                    size=(300, WINDOW_WIDTH),
                    pad=(50, 50),
                ),
                sg.VSeperator(),
                sg.Column([[table]], key="-COLUMN_TABLE-"),
            ]
        ]

        self.layout = new_layout
        window1 = sg.Window(self.title, size=self.window_size).Layout(new_layout)
        self.window.Close()
        self.window = window1
