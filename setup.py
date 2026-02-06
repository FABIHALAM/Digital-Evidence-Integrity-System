import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "flask", "flask_sqlalchemy", "werkzeug", "engine"],
    "excludes": [],
    "include_files": ["templates/", "static/", "uploads/", "reports/"]
}

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
    base = "gui"

setup(
    name="DEIS App",
    version="1.0",
    description="Digital Evidence Integrity System",
    options={"build_exe": build_exe_options},
    executables=[Executable("gui_app.py", base=base)]
)
