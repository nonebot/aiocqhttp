import os
import re
import sys
from dataclasses import dataclass
from typing import List, Optional

api_md_path = sys.argv[1] if len(sys.argv) > 1 \
    else input('输入 CQHTTP 文档的 API.md 路径：\n')
print(api_md_path)

with open(api_md_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.split('## API 列表', maxsplit=1)[1]
content = content.split('## 试验性 API 列表', maxsplit=1)[0]

res = re.findall(r'###\s*`/([_\w]+)`(.+?)\r?\n'
                 r'.*?'
                 r'####\s*参数\r?\n'
                 r'(.+?)'
                 r'####\s*响应数据\r?\n'
                 r'(.+?)(?=\n##)',
                 content,
                 flags=re.MULTILINE | re.DOTALL)

API_METHOD_TEMPLATE = """\
    def {action}(
            self{params}
    ) -> {ret}:
        \"\"\"
        {description}{params_description}
        \"\"\"
        ...
"""


@dataclass
class ApiParam:
    name: str
    type: str
    default: Optional[str]
    description: str

    def __str__(self):
        s = f'{self.name}: {self.type}'
        if self.default:
            s += f' = {self.default}'
        return s

    def docstring(self):
        return f'{self.name}: {self.description}'


@dataclass
class Api:
    action: str
    description: str
    params_str: str
    ret: str

    params: Optional[List[ApiParam]] = None

    def __str__(self):
        params = ''
        params_description = ''
        if self.params:
            params = (',\n' + ' ' * 12).join(
                [', *'] + [str(p) for p in self.params]
            )
            params_description = ('\n' + ' ' * 12).join(
                ['\n\n' +
                 ' ' * 8 + 'Args:'] + [p.docstring() for p in self.params]
            )
        return API_METHOD_TEMPLATE.format(
            action=self.action,
            params=params,
            ret=self.ret,
            description=self.description + '。',
            params_description=params_description
        )


type_mappings = {
    'number': 'int',
    'string': 'str',
    'boolean': 'bool',
    'object': 'Dict[str, Any]',
    'message': 'Message_T',
}

api_list = [Api(*(s.strip() for s in t)) for t in res]

for api in api_list:
    params = re.findall(r'\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|',
                        api.params_str)[2:]
    params = [ApiParam(*(s.strip() for s in p)) for p in params]
    for p in params:
        p.name = p.name.split(maxsplit=1)[0].strip('`')
        p.type = type_mappings[p.type.split(maxsplit=1)[0]]
        p.default = p.default.strip('`')
        if p.default in ('true', 'false'):
            p.default = p.default.capitalize()  # True, False
        elif p.default == '空':
            p.default = "''"  # '' 空字符串
        if p.description.startswith('可选') \
                or '时需要' in p.description \
                or '如不传入' in p.description:
            p.type = f'Optional[{p.type}]'
            if p.default == '-':
                p.default = 'None'
        if p.default == '-':
            p.default = None  # no default value
        p.description = p.description \
            .replace('true', 'True') \
            .replace('false', 'False')
    api.params = params
    if api.ret.startswith('|'):
        api.ret = 'Dict[str, Any]'
    elif '数组' in api.ret:
        api.ret = 'List[Dict[str, Any]]'
    elif api.ret == '无':
        api.ret = 'None'
    else:
        api.ret = 'Any'

os.chdir(os.path.dirname(os.path.dirname(__file__)) or '.')

with open(os.path.join('scripts', 'api.pyi.template'),
          'r', encoding='utf-8') as f:
    stub_template = f.read()

api_methods = '\n'.join([str(api) for api in api_list])
print(api_methods)
with open(os.path.join('aiocqhttp', 'api.pyi'), 'w', encoding='utf-8') as f:
    f.write(stub_template.format(api_methods=api_methods))
