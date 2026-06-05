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

本程序用于从 `.sas` 文件中裁剪需要递交的代码，并以 `.txt` 格式存储，可处理单个文件，也可以处理指定目录下的所有文件。

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

> [!NOTE]
>
> 对于 Windows 用户，你可以在 `%LOCALAPPDATA%/Programs/Python/Python313/Scripts` 中看到 `submit.exe`，你在终端执行 `submit` 命令实际上调用的是这个程序。

## 使用方法

`submit` 包含两个子命令：

- `copyfile`: 处理单个 sas 文件，保存处理后的代码到 txt 文件中
- `copydir`: 处理指定目录下的所有 sas 文件，保存处理后的代码到指定目录中

`submit` 命令会识别 `.sas` 文件中的特殊注释，根据这些注释裁剪代码片段，以满足递交需求。

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

## 选项参考

### 子命令 `copyfile`

子命令 `copyfile` 用于处理单个 `.sas` 文件，可用的选项如下：

#### `-s, -sas-file`

指定需裁剪的 `.sas` 文件路径，可以使用相对路径和绝对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

#### `-t, -txt-file`

指定处理后的代码保存的 `.txt` 文件路径，可以使用相对路径和绝对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

#### `--positive`

指定处理 _positive_ 模式的注释。

#### `--no-positive`

指定不要处理 _positive_ 模式的注释。

#### `--negative`

指定处理 _negative_ 模式的注释，优先级高于 `--positive`。

#### `--no-negative`

指定不要处理 _negative_ 模式的注释。

#### `-e, --encoding`

指定 `.sas` 文件的字符编码，默认值为 `gbk`。

#### `--help`

显示帮助信息并退出。

#### 示例

```bash
submit copyfile -s "./adae.sas" "./output/adae.txt"
submit copyfile -s "./adae.sas" "./output/adae.txt" --no-negative
submit copyfile -s "./adae.sas" "./output/adae.txt" --no-negative --encoding utf-8
```

### 子命令 `copydir`

```bash
Usage: submit copydir [OPTIONS]

  处理指定目录下的所有 sas 文件，保存处理后的代码到指定目录中。

Options:
  -s, --sas-dir DIRECTORY     包含需裁剪的 sas 代码的目录路径  [required]
  -t, --txt-dir PATH          裁剪后的 sas 代码保存的目录路径  [required]
  --positive / --no-positive  是否处理 positive 模式的注释
  --negative / --no-negative  是否处理 negative 模式的注释，优先级高于 --positive
  -e, --encoding TEXT         字符编码，默认值为 gbk
  --merge / --no-merge        是否将所有处理后的代码合并到一个文件中
  --merge-name TEXT           合并后的文件名，默认值为 merged.txt，仅当 --merge 选项为 True 时有效
  -exd, --exclude-dir TEXT    排除的目录路径模式
  -exf, --exclude-file TEXT   排除的文件路径模式
  --help                      Show this message and exit.
```

子命令 `copydir` 用于处理包含 `.sas` 文件的目录，该命令将以递归的方式自动查找扩展名为 `.sas` 的文件并进行处理，非 `.sas` 文件将被忽略。

可用的选项如下：

#### `-s, --sas-dir`

指定包含需裁剪的 sas 代码的目录路径，可以使用相对路径和绝对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

#### `-t, --txt-dir`

指定裁剪后的 sas 代码保存的目录路径，可以使用相对路径和绝对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

#### `--positive`

同 [--positive](#--positive)

#### `--no-positive`

同 [--no-positive](#--no-positive)

#### `--negative`

同 [--negative](#--negative)

#### `--no-negative`

同 [--no-negative](#--no-negative)

#### `-e, --encoding`

同 [`--encoding`](#--encoding)

#### `--merge`

指定是否将所有处理后的代码合并到一个文件中。

> [!NOTE]
>
> 合并后的 `.txt` 文件包含源目录中所有需要递交的 sas 代码，使用注释 `/*====================`_`filename`_`.sas====================*/` 分隔来自不同 `.sas` 文件的代码。
> 其中 _`filename`_ 是源目录中 `.sas` 文件名称。

> [!IMPORTANT]
>
> 某些地方医疗器械监督管理局不接收压缩包作为递交文件，且递交文件数量存在限制，因此必须将所有 `.sas` 文件合并成一个单独的 `.txt` 文件。

#### `--merge-name`

指定合并后的文件名，默认值为 `merged.txt`，仅当指定了 `--merge` 选项时有效。

#### `-exd, --exclude-dir`

指定需排除的目录的 [glob 路径模式](#glob-模式介绍)，所有匹配该模式的目录中的 `.sas` 文件将被忽略。

该选项可以多次使用，表示多个排除目录。

#### `-exf, --exclude-file`

指定需排除的文件的 [glob 路径模式](#glob-模式介绍)，所有匹配该模式的文件将被忽略。

该选项可以多次使用，表示多个排除文件。

#### 示例

```bash
submit copydir "./adam" "./adam/output"
submit copydir "./adam" "./adam/output" --exclude-file "**/deprecated*.sas"
submit copydir "./adam" "./adam/output" --exclude-file "**/deprecated*.sas" --exclude-dir "sponser-only" --exclude-dir "test-only"
submit copydir "./adam" "./adam/output" --merge --merge-name "all.txt"
```

### glob 模式介绍

`glob` 是一种使用通配符指定文件（目录）名称集合的模式，查看 [wiki](<https://en.wikipedia.org/wiki/Glob_(programming)>)。

你可以在路径中使用以下特殊字符作为通配符：

- `*`: 匹配任意数量的非分隔符型字符，包括零个。例如，`f*.sas` 匹配 `f1.sas`、`f2.sas`、`f3.sas` 等等。
- `**`: 匹配任意数量的文件或目录分段，包括零个。例如，`**/f*.sas` 匹配 `figure/f1.sas`、`figure/f2.sas`、`figure/draft/f1.sas` 等等。
- `?`: 匹配一个不是分隔符的字符。例如，`t1?.sas` 匹配 `t1.sas`、`t10.sas`、`t11.sas` 等等。
- `[seq]`: 匹配在 seq 中的一个字符。例如，`[tfl]1.sas` 匹配 `t1.sas`、`f1.sas`、`l1.sas`。

更多语法请查看 [模式语言](https://docs.python.org/zh-cn/3/library/pathlib.html#pattern-language)。

假设有这样一个文件目录结构：

```
D:.
├─source
│  ├─f1.sas
│  ├─f2.sas
│  ├─f2-deprecated.sas
│  ├─f3.sas
│  ├─f3-deprecated.sas
│  ├─t1.sas
│  ├─t2.sas
│  ├─t2-deprecated.sas
│  ├─t2-deprecated-20241221.sas
│  ├─t3.sas
│  ├─t4.sas
│  ├─t5.sas
│  ├─t5-deprecated.sas
│  ├─t6.sas
│  ├─t7.sas
│  └─t7-deprecated.sas
└─dest
```

现在需要将 `source` 目录中的 `.sas` 文件转换为 `.txt` 文件，但忽略名称包含 `deprecated` 的文件，可以使用以下命令：

```bash
submit copydir --s "~/source" -t "~/dest" --exclude-file "*deprecated*.sas"
```

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
