call conda activate Product

set target=__main__
set target_name=JsonViewer
set prefix=JsonViewer/
set target_path=%prefix%%target_name%.py
set output_dir=dist/

python -m nuitka --mingw64 ^
--onefile ^
--include-package=JsonViewer ^
--enable-plugin=pyside6 ^
--windows-icon-from-ico=ui_resources/icons/jsViewer.png ^
--windows-disable-console ^
--output-dir=%output_dir% ^
--show-progress ^
--lto=no ^
%target_path%

pause
```