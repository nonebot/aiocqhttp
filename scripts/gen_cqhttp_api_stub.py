import sys
import re
from os import path
from itertools import islice
from textwrap import indent
from dataclasses import dataclass
from typing import List, Optional, Tuple


TypeStr = str

type_mappings = {
    "number": "int",
    "number (int32)": "int",
    "number (int64)": "int",
    "string": "str",
    "boolean": "bool",
    "object": "Dict[str, Any]",
    "array": "List[Any]",
    "message": "Message_T",
    "-": "Any",
}


@dataclass
class ApiParam:
    name: str
    type_: TypeStr
    default: Optional[str]
    description: str

    def render(self):
        s = f"{self.name}: {self.type_}"
        if self.default is not None:
            s += f" = {self.default}"
        return s

    def docstring(self):
        return f"{self.name}: {self.description}"


@dataclass
class ApiReturn:
    action: str
    fields: List[Tuple[str, TypeStr]]
    is_array: bool

    @property
    def _base(self):
        return f"_{self.action}_ret"

    @property
    def var_name(self):
        if self.is_array:
            return f"List[{self._base}]"
        return self._base

    def render_definition_38(self):
        return f"class {self._base}(TypedDict):\n" + "\n".join(
            f"    {name}: {type_}" for name, type_ in self.fields
        )

    def render_definition_37(self):
        return f'{self._base} = {type_mappings["object"]}'


@dataclass
class Api:
    action: str
    description: str

    ret: Optional[ApiReturn]
    params: Optional[List[ApiParam]]

    def _get_param_specs(self):
        params = "self,"
        arg_docs = "无"
        ret = "None"
        if self.params is not None:
            params = "self, *,\n"
            params += "\n".join(f"{p.render()}," for p in self.params)
            arg_docs = "\n".join(f"{p.name}: {p.description}" for p in self.params)
        if self.ret is not None:
            ret = self.ret.var_name
        return params, arg_docs, ret

    def render_definition(self):
        params, arg_docs, ret = self._get_param_specs()
        return (
            f"def {self.action}(\n"
            f'{indent(params, " " * 8)}\n'
            f") -> Union[Awaitable[{ret}], {ret}]:\n"
            f'    """\n'
            f"    {self.description}。\n"
            f"\n"
            f"    Args:\n"
            f'{indent(arg_docs, " " * 8)}\n'
            f'    """'
        )

    def render_definition_async(self):
        params, _, ret = self._get_param_specs()
        return (
            f"async def {self.action}(\n"
            f'{indent(params, " " * 8)}\n'
            f") -> {ret}: ..."
        )

    def render_definition_sync(self):
        params, _, ret = self._get_param_specs()
        return f"def {self.action}(\n" f'{indent(params, " " * 8)}\n' f") -> {ret}: ..."


def create_params(param_block: str):
    params = []
    if param_block.strip() == "无":
        params.append(ApiParam("self_id", "Optional[int]", "None", "机器人 QQ 号"))
        return params
    if re.search(
        r"^\|\s*字段名\s*\|\s*数据类型\s*\|\s*默认值\s*\|\s*说明\s*\|", param_block, re.MULTILINE
    ):
        rows = re.findall(
            r"^\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|", param_block, re.MULTILINE
        )
    else:  # ^| 字段名 | 数据类型 | 说明 |
        rows = re.findall(r"^\|([^|]+)\|([^|]+)\|([^|]+)\|", param_block, re.MULTILINE)
    for row in islice(rows, 2, None):
        name = row[0].split()[0].strip(" `")  # `xxx` 或 `yyy`
        type_ = type_mappings[row[1].strip()]
        if len(row) == 3:
            default = None
            pdesc = row[2].strip()
        else:
            default = row[2].strip(" `")
            pdesc = row[3].strip()
        if pdesc.startswith("可选") or "时需要" in pdesc or "如不传入" in pdesc:
            type_ = f"Optional[{type_}]"
            if default == "-":
                default = "None"
        if default == "-":
            default = None
        if default == "空":
            default = "''"
        if default in ("true", "false"):
            default = default.capitalize()
        pdesc = pdesc.replace("true", "True").replace("false", "False")
        params.append(ApiParam(name, type_, default, pdesc))
    params.append(ApiParam("self_id", "Optional[int]", "None", "机器人 QQ 号"))
    return params


def create_ret(action: str, ret_block: str):
    # content until first table
    ret_block_head = next(re.finditer(r"^[^|]*", ret_block))[0].strip()
    if ret_block_head == "无":
        return None
    is_array = "数组" in ret_block_head
    first = True
    ret = None
    # there might be multiple tables
    for table_block in re.findall(
        r"\|\s*字段名.+?(?=(?=\n\n)|(?=$))", ret_block, re.DOTALL
    ):
        fields = []
        for row in islice(
            re.findall(r"^\|([^|]+)\|([^|]+)\|([^|]+)\|", table_block, re.MULTILINE),
            2,
            None,
        ):
            name = row[0].strip(" `")
            if name == "……":
                name = "#__there_might_be_more_fields_below"
            type_ = type_mappings[row[1].strip()]
            fields.append((name, type_))
        if first:
            ret = ApiReturn(action, fields, is_array)
            first = False
        else:
            print(
                f"Found extra return tables in {action}. "
                "Typeddict is given below:\n"
                f'{ApiReturn("_", fields, is_array).render_definition_38()}'
            )
    if ret is None:
        # fix me later in the output!
        ret = ApiReturn(action, [("", "I AM BROKEN. WATCH ME!!")], is_array)
        print(f"Api {action} is broken. Needs manual action")
    return ret


def create_apis(fn: str) -> List[Api]:
    apis = []
    section_blocks = re.findall(
        r"##\s*`([_\w]+)`\s*(.+?)\r?\n"
        r".*?\n"
        r"###\s*参数\r?\n"
        r"(.+?)\n"
        r"###\s*响应数据\r?\n"
        r"(.+?)(?=\n(?=##)|(?=<hr>))",
        open(fn).read(),
        flags=re.MULTILINE | re.DOTALL,
    )

    for action, desc, param_block, ret_block in section_blocks:
        params = create_params(param_block)
        ret = create_ret(action, ret_block)
        apis.append(Api(action, desc, ret, params))
    return apis


if len(sys.argv) < 3:
    sys.stderr.write(f"Usage: {sys.argv[0]} <api-doc-file> <output-file>\n")
    exit(1)

template_path = path.join(path.dirname(__file__), "api.pyi.template")
with open(template_path) as template_in, open(sys.argv[2], "w") as of:
    apis = create_apis(sys.argv[1])
    api_returns_38 = "\n\n".join(
        api.ret.render_definition_38() for api in apis if api.ret is not None
    )
    api_returns_37 = "\n".join(
        api.ret.render_definition_37() for api in apis if api.ret is not None
    )
    api_methods = "\n\n".join(api.render_definition() for api in apis)
    api_methods_async = "\n\n".join(api.render_definition_async() for api in apis)
    api_methods_sync = "\n\n".join(api.render_definition_sync() for api in apis)
    of.write(
        template_in.read().format(
            api_returns_38=indent(api_returns_38, " " * 4),
            api_returns_37=indent(api_returns_37, " " * 4),
            api_methods=indent(api_methods, " " * 4),
            api_methods_async=indent(api_methods_async, " " * 4),
            api_methods_sync=indent(api_methods_sync, " " * 4),
        )
    )
