from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from user_interface import Ui_window

import util


class GuiManager(QMainWindow):
    def __init__(self, controller):
        super(GuiManager, self).__init__()

        self.controller = controller

        # init window
        self.ui_window = Ui_window()
        self.ui_window.setupUi(self)

        # set tables settings
        self.ui_window.cache_contents_table.setVisible(False)
        self.ui_window.operations_table.setVisible(False)
        self.ui_window.operations_table.itemClicked.connect(self.change_cache_contents)

        # set button actions
        self.ui_window.create_button.clicked.connect(self.create_button_press)
        self.ui_window.start_button.clicked.connect(self.start_button_press)

        self.setWindowTitle("Cache Simulation")

        self.show()

    def create_button_press(self):

        # TODO : some sort of validation is needed

        block_size = int(self.ui_window.block_size_input.text())
        cache_capacity = int(self.ui_window.cache_capacity_input.text())
        ram_capacity = int(self.ui_window.ram_capacity_input.text())

        associativity_combo_box = self.ui_window.associativity_combo_box.currentText()
        if associativity_combo_box == "Directly Mapped":
            associativity = util.DIRECTLY_MAPPED
        elif associativity_combo_box == "Fully Associative":
            associativity = util.FULLY_ASSOCIATIVE
        else:
            associativity = self.ui_window.nway_input.text() + "-WAY"

        replacement_combo_box = (
            self.ui_window.replacement_strategy_combo_box.currentText()
        )
        if replacement_combo_box == "Random":
            replacement_strategy = util.ReplacementStrategy.RANDOM
        elif replacement_combo_box == "FIFO":
            replacement_strategy = util.ReplacementStrategy.FIRST_IN_FIRST_OUT
        elif replacement_combo_box == "Least Frequently Used":
            replacement_strategy = util.ReplacementStrategy.LEAST_FREQUENTLY_USED
        elif replacement_combo_box == "Least Recently Used":
            replacement_strategy = util.ReplacementStrategy.LEAST_RECENTLY_USED
        elif replacement_combo_box == "Most Recently Used":
            replacement_strategy = util.ReplacementStrategy.MOST_RECENTLY_USED

        write_combo_box = self.ui_window.write_policy_combo_box.currentText()
        if write_combo_box == "Write Once":
            write_policy = util.WritePolicy.WRITE_ONCE
        elif write_combo_box == "Write Through":
            write_policy = util.WritePolicy.WRITE_THROUGH
        elif write_combo_box == "Write Back":
            write_policy = util.WritePolicy.WRITE_BACK

        self.controller.create_cache(
            cache_capacity,
            associativity,
            block_size,
            replacement_strategy,
            write_policy,
        )
        self.controller.create_ram(ram_capacity, block_size)
        self.controller.fill_cache()

        self.populate_table()

    def start_button_press(self):

        headers = ["Operation", "Tag", "Index", "Result"]

        operations = [("cache creation", "", "", "")]

        operations = operations + self.controller.read_and_write_all_blocks_once()

        operations = operations + self.controller.read_and_write_blocks_randomly()

        operations = operations + self.controller.replace_blocks()

        table = self.ui_window.operations_table

        table.setRowCount(0)
        table.setColumnCount(0)

        table.setRowCount(len(operations))
        table.setColumnCount(4)

        # insert headers
        for index, heading in enumerate(headers):
            table.setItem(0, index, QTableWidgetItem(heading))

        # insert values
        for operation_index, operation in enumerate(operations):
            for index, operation_attribute in enumerate(operation):
                table.setItem(
                    operation_index, index, QTableWidgetItem(str(operation_attribute))
                )

        table.setHorizontalHeaderLabels(headers)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setVisible(True)

    def change_cache_contents(self, item):
        headings, values = self.controller.cache_records[item.row()]
        self.populate_table(headings, values)

    def populate_table(self, headings=None, values=None):

        if not headings or not values:
            headings, values = self.controller.fetch_cache_data()

        table = self.ui_window.cache_contents_table

        table.setRowCount(0)
        table.setColumnCount(0)

        table.setRowCount(len(values))
        table.setColumnCount(len(headings))

        # insert headers
        for index, heading in enumerate(headings):
            table.setItem(0, index, QTableWidgetItem(heading))

        # insert values
        for line_index, line_value in enumerate(values):

            for index, value in enumerate(line_value):
                table.setItem(line_index, index, QTableWidgetItem(str(value)))

        table.setHorizontalHeaderLabels(headings)
        table.verticalHeader().setVisible(False)

        header = table.horizontalHeader()
        for i, _ in enumerate(headings):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)

        table.setVisible(True)
