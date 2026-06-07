# submit.py

![requires-python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fsmjc-org%2Fpy-submit%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsmjc-org%2Fpy-submit%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&query=%24.project.version&label=version)
![GitHub License](https://img.shields.io/github/license/smjc-org/py-submit)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com/)
[![pytest](https://github.com/smjc-org/py-submit/actions/workflows/pytest.yml/badge.svg)](https://github.com/smjc-org/py-submit/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/smjc-org/py-submit/graph/badge.svg?token=MNWAUJ35HT)](https://codecov.io/gh/smjc-org/py-submit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/smjc-org/py-submit/main.svg)](https://results.pre-commit.ci/latest/github/smjc-org/py-submit/main)

本程序用于从 `.sas` 文件中裁剪需要递交的代码，并以 `.txt` 格式存储，支持单文件和多文件处理。

## 安装

首先安装 [Python](https://www.python.org/downloads/) 和 [Git](https://git-scm.com)

然后使用 `pip` 命令安装指定版本，例如：

```bash
pip install git+https://github.com/smjc-org/py-submit.git@0.5.6
```

或者从特定 commit 安装：

```bash
pip install git+https://github.com/smjc-org/py-submit.git@5ed1b3d545c5670f110fe32139860e8e5a9f446b
```

上述命令会将本程序安装到环境变量中指定的目录下，并向系统注册 `submit` 命令以供后续调用。

## 使用方法

`submit` 包含两个子命令：

- `copyfile`: 处理单个 sas 文件，保存处理后的代码到 txt 文件中
- `copydir`: 处理指定目录下的所有 sas 文件，保存处理后的代码到指定目录中

程序会识别 `.sas` 文件中的特殊注释，根据这些注释裁剪代码片段，以满足递交需求。

可识别的注释分为两类：_positive_ 模式和 _negative_ 模式。

***positive*** 模式的注释格式为：

- /* _symbols_ `SUBMIT BEGIN` _symbols_ */
- /* _symbols_ `SUBMIT END` _symbols_ */

***negative*** 模式的注释格式为：

- /* _symbols_ `NOT SUBMIT BEGIN` _symbols_ */
- /* _symbols_ `NOT SUBMIT END` _symbols_ */

> [!NOTE]
>
> - _`symbols`_ 可以是符号 `*`, `-`, `=`, ` `(空格) 的任意组合
> - 注释不区分大小写

举例，假设文件 `code.sas` 的内容如下：

```sas
proc datasets library = work memtype = data kill noprint;
quit;

dm ' log; clear; output; clear; odsresult; clear; ';

/*SUBMIT BEGIN*/
proc sql noprint;
    create table work.adsl as select * from rawdata.adsl;
quit;

/*NOT SUBMIT BEGIN*/
proc sql noprint;
    create table work.t_6_1_1 as select * from adsl;
quit;
/*NOT SUBMIT END*/

proc means data = adsl;
run;

/*SUBMIT END*/

%log;
%error;
```

使用以下命令处理 `code.sas` 文件：

```bash
submit copyfile -s code.sas -t code.txt
```

处理后的代码保存在 `code.txt` 中：

```sas
proc sql noprint;
    create table work.adsl as select * from rawdata.adsl;
quit;


proc means data = adsl;
run;
```

更多选项及其用法请参考 [CLI](./docs/usage.md)。

## 如何贡献

前置条件：

- [Python](https://www.python.org/downloads/) >= 3.12
- [Git](https://git-scm.com/downloads) >= 2.45
- [uv](https://docs.astral.sh/uv/getting-started/installation/) >= 0.5.9

1. 克隆仓库代码

   ```bash
   git clone https://github.com/smjc-org/py-submit.git
   ```

2. 安装依赖

   ```bash
   uv sync --all-groups
   ```

3. 修改代码

4. 测试代码

   ```bash
   uv run pytest
   ```

5. 发起 pull request

> [!NOTE]
>
> 1. 推荐使用 [VSCode](https://code.visualstudio.com/Download) 编辑代码
> 2. 需要使用 [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) 规范的提交信息
