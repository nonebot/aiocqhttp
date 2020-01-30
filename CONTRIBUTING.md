# 贡献指南

## 安装

首先 fork 本项目，然后克隆并安装：

```bash
git clone git@github.com:YOUR_USERNAME/python-aiocqhttp
cd python-aiocqhttp
pip install -e .   # 注意点号
```

## 测试

目前本项目没有单元测试。如需贡献新功能或修复 bug，请在提交 PR 之前做好测试，并在 PR 中提供测试过程和结果。

## 代码风格

请使用 Flake8 确保代码符合 PEP 8：

```bash
flake8 aiocqhttp
```

另外，变量、函数、类、方法、模块等的命名应与项目其它部分一致，且含义清晰。

## 文档

项目文档在 `docs` 目录，其中子目录 `module` 中的模块 API 文档是由 [pdoc](https://github.com/pdoc3/pdoc) 自动生成的。

当新增了用户可见的变量、函数、类、方法、模块等时，应当使用 pdoc 所支持的格式编写 docstring（使用中文）。

其中，当需要书写行内代码时，对于模块名、函数名、类名等潜在可能链接到模块 API 文档其它部分的内容，使用单个反引号（<code>`</code>）括起，pdoc 将自动生成链接；而对于变量名、函数形参名、变量可能的取值等不可能链接到模块 API 文档其它部分的内容，使用两个反引号括起（<code>``</code>）。

## 提交 PR

在你 fork 的仓库的「Pull requests」页面，点「New pull request」可提交 PR，具体细节请参考网上教程。

请在 PR 中解释该 PR 所做的事情，和相关测试结果等。

最后，感谢你的贡献！
