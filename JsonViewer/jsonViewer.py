import json

import yaml
from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from PySide6.QtGui import QStandardItem, QStandardItemModel, QColor, QIcon, QAction
from PySide6.QtWidgets import QTreeView, QStyledItemDelegate, QMenu, QApplication, QFileDialog, QMainWindow, \
    QMessageBox, QVBoxLayout, QDialog, QTextEdit
from typing import TYPE_CHECKING
import chardet
import resources_rc

if TYPE_CHECKING:
    print(resources_rc)

class JsonItemDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        font_size = option.font.pointSize() - 2
        option.font.setPointSize(font_size)
        option.font.setFamily("Consolas")


class JsonViewerWidget(QTreeView):
    def __init__(self, json_data):
        super().__init__()
        self.setWindowTitle("Json Viewer")
        self.setHeaderHidden(True)
        self.setIndentation(20)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(True)
        self.setEditTriggers(QTreeView.NoEditTriggers)

        self.setModel(self._create_model(json_data))
        self.expandAll()

        self._current_animation = None

    def set_json_data(self, json_data):
        self.setModel(self._create_model(json_data))
        self.expandAll()

    def _create_model(self, json_data):
        model = QStandardItemModel()
        self._add_json_data(model, json_data)
        delegate = JsonItemDelegate()
        for i in range(model.columnCount()):
            self.setItemDelegateForColumn(i, delegate)
        return model

    def _add_json_data(self, parent_item, data, depth=0):
        if isinstance(data, dict):
            for key, value in data.items():
                key_item = QStandardItem(str(key))
                font_size = 20 - depth
                font = key_item.font()
                font.setPointSize(font_size)
                key_item.setFont(font)
                if isinstance(value, dict):
                    icon = QIcon(":/icons/icons/icons8-curly-brackets-50.png")
                elif isinstance(value, list):
                    icon = QIcon(":/icons/icons/icons8-list-50.png")
                else:
                    icon = QIcon(":/icons/icons/icons8-key-96.png")
                key_item.setData(icon, Qt.DecorationRole)
                parent_item.appendRow(key_item)
                self._add_json_data(key_item, value, depth + 1)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    group_item = QStandardItem()
                    group_item.setFlags(Qt.NoItemFlags)
                    font_size = 20 - depth
                    font = group_item.font()
                    font.setPointSize(font_size)
                    group_item.setFont(font)
                    group_item.setData(QIcon(":/icons/icons/icons8-curly-brackets-50.png"), Qt.DecorationRole)
                    parent_item.appendRow(group_item)

                    action = QAction("Collapse", self)
                    action.triggered.connect(self._toggle_group_item)
                    group_item.setData(action, Qt.UserRole)

                    # for key, value in item.items():
                    #     key_item = QStandardItem(str(key))
                    #     font_size = 20 - depth - 1
                    #     font = key_item.font()
                    #     font.setPointSize(font_size)
                    #     key_item.setFont(font)
                    #     group_item.appendRow(key_item)
                    #     self._add_json_data(key_item, value, depth + 2)
                    self._add_json_data(group_item, item, depth + 2)

                else:
                    value_item = QStandardItem(str(item))
                    font_size = 20 - depth - 1
                    font = value_item.font()
                    font.setPointSize(font_size)
                    value_item.setFont(font)
                    value_item.setData(QIcon(":icons/icons/icons8-negative-24.png"), Qt.DecorationRole)
                    parent_item.appendRow(value_item)
        else:
            value_item = QStandardItem(str(data))
            font_size = 20 - depth - 1
            font = value_item.font()
            font.setPointSize(font_size)
            value_item.setFont(font)
            value_item.setData(QIcon(":icons/icons/icons8-negative-24.png"), Qt.DecorationRole)
            parent_item.appendRow(value_item)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid() and event.button() == Qt.RightButton:
            menu = QMenu(self)
            if index.parent().isValid() and not index.parent().parent().isValid():
                action = QAction("Delete", self)
                action.triggered.connect(self._delete_item)
                menu.addAction(action)
            menu.exec_(event.globalPos())
        else:
            super().mousePressEvent(event)

    def _toggle_group_item(self, index):
        item = self.sender().parent()
        if item.isExpanded():
            self._current_animation = QPropertyAnimation(self, b"geometry")
            self._current_animation.setDuration(200)
            self._current_animation.setStartValue(self.visualRect(item.index()))
            self._current_animation.setEndValue(QRect(0, 0, 0, 0))
            self._current_animation.finished.connect(lambda: item.setExpanded(False))
            self._current_animation.start()
        else:
            item.setExpanded(True)
            self.scrollTo(index)
            self._current_animation = QPropertyAnimation(self, b"geometry")
            self._current_animation.setDuration(200)
            self._current_animation.setStartValue(QRect(0, 0, 0, 0))
            self._current_animation.setEndValue(self.visualRect(index))
            self._current_animation.start()

    def _delete_item(self):
        index = self.currentIndex()
        if index.isValid() and index.parent().isValid():
            parent = self.model().itemFromIndex(index.parent())
            parent.removeRow(index.row())

    def current_animation(self):
        return self._current_animation

# a main window containing a button to select the json file
class JsonViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Json Viewer")
        self.setWindowIcon(QIcon(":/icons/icons/jsViewer.png"))

        self.jsViewer = JsonViewerWidget({})
        self.setCentralWidget(self.jsViewer)
        self.resize(640, 480)

        self._create_menu()

    def _create_menu(self):
        menu = self.menuBar().addMenu("File")
        actionOpen = QAction("Open", self)
        actionOpen.triggered.connect(self._open_file)
        menu.addAction(actionOpen)

        editMenu = self.menuBar().addMenu("Edit")

        self.menuBar().addAction("Exit", self.close)
        self.menuBar().addAction("Help", self._help)

    def _open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Notation Files (*.json *.yaml *.yml);;All Files (*.*)")
        if file_name:
            encode = chardet.detect(open(file_name, "rb").read())["encoding"]
            with open(file_name, "r", encoding=encode) as f:
                if file_name.endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            self.jsViewer.set_json_data(data)

    def _help(self):
        # QMessageBox.about(self, "Help", "This is a Json Viewer. You can open a json file and view it."
        #                                 " You can also edit the json file and save it.")
        #
        # show a dialog box for showing help information
        # in the pop-up window, the user will see several icons used in this app and their meanings
        # the user can click on the icon to see the meaning of the icon

        helpDialog = QDialog(self)
        helpDialog.setWindowTitle("Help")
        helpDialog.setWindowIcon(QIcon(":/icons/icons/jsViewer.png"))
        helpDialog.resize(400, 300)
        helpDialog.setModal(True)
        helpDialog.setLayout(QVBoxLayout())

        helpText = QTextEdit()
        helpText.setReadOnly(True)

        # fixed size images
        helpText.setHtml("""
        <h1>Json Viewer</h1>
        <p>This is a Json Viewer. You can open a json file and view it. You can also edit the json file and save it.</p>
        <h2>Icons</h2>
        <p><img src=":/icons/icons/icons8-curly-brackets-50.png" width="24" height="24"> Dict Children</p>
        <p><img src=":/icons/icons/icons8-key-96.png" width="24" height="24"> Single Value Children</p>
        <p><img src=":/icons/icons/icons8-list-50.png" width="24" height="24"> List Children</p>
        <p><img src=":/icons/icons/icons8-negative-24.png" width="24" height="24"> No Children</p>
        """)
        helpDialog.layout().addWidget(helpText)
        helpDialog.exec()


    def closeEvent(self, event):
        if self.jsViewer.current_animation():
            event.ignore()
        else:
            super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.jsViewer.collapseAll()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.jsViewer.collapseAll()
        else:
            super().mousePressEvent(event)

    def resizeEvent(self, event):
        if self.jsViewer.current_animation():
            event.ignore()
        else:
            super().resizeEvent(event)

    def showEvent(self, event):
        if self.jsViewer.current_animation():
            event.ignore()
        else:
            super().showEvent(event)

    def wheelEvent(self, event):
        if self.jsViewer.current_animation():
            event.ignore()
        else:
            super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        if self.jsViewer.current_animation():
            event.ignore()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.jsViewer.current_animation():
            event.ignore()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.jsViewer.current_animation():
            event.ignore()
        else:
            super().mouseDoubleClickEvent(event)




if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # window = JsonViewerWidget({
    #     "name": "John",
    #     "age": 30,
    #     "cars": [
    #         {
    #             "name": "Ford",
    #             "models": ["Fiesta", "Focus", "Mustang"]
    #         },
    #         {
    #             "name": "BMW",
    #             "models": ["320", "X3", "X5"]
    #         },
    #         {
    #             "name": "Fiat",
    #             "models": ["500", "Panda"]
    #         }
    #     ]
    # })
    window = JsonViewerWindow()
    window.show()
    sys.exit(app.exec())
