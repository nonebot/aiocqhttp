import os
import sys

os.system(sys.executable +
          ' -m pdoc'
          '   --html'
          '   -o docs/module'
          '   -c html_lang="\'zh\'"'
          '   -c show_type_annotations=True'
          '   -c show_inherited_members=True'
          '   -c sort_identifiers=False'
          '   -f'
          '   aiocqhttp')
