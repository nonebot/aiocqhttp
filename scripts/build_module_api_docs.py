import os
import sys

os.chdir(os.path.dirname(os.path.dirname(__file__)) or ".")

os.system(
    sys.executable + " -m pdoc"
    " --html"
    " -o docs/module"  # cwd should be project dir
    " -c html_lang=\"'zh'\""
    " -c show_type_annotations=True"
    " -c show_inherited_members=True"
    " -c sort_identifiers=False"
    " -f"
    " aiocqhttp"
)
