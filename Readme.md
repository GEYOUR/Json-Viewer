# Json-Viewer

Json-Viewer is a small application that displays JSON data in a hierarchical tree structure. It allows users to expand and collapse nodes and provides animations to make the user interface more user-friendly.

## Installation

To use Json-Viewer, you need to install PySide6, which is a Python binding for the Qt application framework. You can install it using pip:

```
pip install PySide6

```

## Usage

You can use Json-Viewer in your Python code by creating an instance of the `JsonViewerWidget` class and passing a JSON object as a parameter. Here is an example:

```python
from PySide6.QtWidgets import QApplication
from json_viewer import JsonViewerWidget

if __name__ == '__main__':
    app = QApplication([])
    json_data = {
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
    }
    widget = JsonViewerWidget(json_data)
    widget.show()
    app.exec()

```

## Future Development

In addition to its current functionality, Json-Viewer is scheduled to support more JSON-related functions, such as editing and validating JSON data.

## Contributing

Contributions to Json-Viewer are welcome! If you find a bug or have a feature request, please open an issue on the [GitHub repository](https://github.com/your-username/json-viewer/issues). If you want to contribute code, please fork the repository and submit a pull request.

## License

Json-Viewer is licensed under the [MIT License](https://github.com/your-username/json-viewer/blob/main/LICENSE).