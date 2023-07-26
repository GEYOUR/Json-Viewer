from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from PySide6.QtGui import QStandardItem, QStandardItemModel, QColor, QIcon, QAction
from PySide6.QtWidgets import QTreeView, QStyledItemDelegate, QMenu, QApplication
import ui_resources.resources_rc

class JsonItemDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        font_size = option.font.pointSize() - 2
        option.font.setPointSize(font_size)


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
        self.setModel(self._create_model(json_data))

        self.setEditTriggers(QTreeView.NoEditTriggers)

        self.expandAll()

        self._current_animation = None

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
                key_item.setData(QIcon(":/icons/icons/icons8-list-50.png"), Qt.DecorationRole)
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

                    for key, value in item.items():
                        key_item = QStandardItem(str(key))
                        font_size = 20 - depth - 1
                        font = key_item.font()
                        font.setPointSize(font_size)
                        key_item.setFont(font)
                        group_item.appendRow(key_item)
                        self._add_json_data(key_item, value, depth + 2)
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

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = JsonViewerWidget({
        "name": "John",
        "age": 30,
        "cars": [
            {
                "name": "Ford",
                "models": ["Fiesta", "Focus", "Mustang"]
            },
            {
                "name": "BMW",
                "models": ["320", "X3", "X5"]
            },
            {
                "name": "Fiat",
                "models": ["500", "Panda"]
            }
        ]
    })
    window.show()
    sys.exit(app.exec())
