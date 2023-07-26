set target=__main__
set target_name=JsonViewer
set prefix=JsonViewer/
set target_path=%prefix%%target_name%.py
set output_dir=dist/

python -m nuitka --mingw64 ^
--standalone ^
--enable-plugin=pyside6 ^
--include-package=JsonViewer ^
--windows-icon-from-ico=ui_resources/icons/jsViewer.png ^
--output-dir=%output_dir% ^
--windows-disable-console ^
--show-progress ^
--lto=no ^
%target_path%

pause
```