# submit.py

![requires-python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fsmjc-org%2Fpy-submit%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsmjc-org%2Fpy-submit%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&query=%24.project.version&label=version)
![GitHub License](https://img.shields.io/github/license/smjc-org/py-submit)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com/)
[![pytest](https://github.com/smjc-org/py-submit/actions/workflows/pytest.yml/badge.svg)](https://github.com/smjc-org/py-submit/actions/workflows/pytest.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/smjc-org/py-submit/main.svg)](https://results.pre-commit.ci/latest/github/smjc-org/py-submit/main)

本程序用于从 `.sas` 文件中提取需要递交至监管机构的代码，并另存为 `.txt` 格式的文件。

## 安装

在终端中执行以下命令：

```bash
pip install git+https://github.com/smjc-org/py-submit.git@main
```

该命令将会在系统中注册 `submit` 命令，以便后续使用。

> [!IMPORTANT]
>
> 你需要先安装 [Python](https://www.python.org/downloads/) 和 [Git](https://git-scm.com/downloads) 才能执行以上命令。

## 如何使用

`submit` 命令会识别 `.sas` 文件中的特殊注释，根据这些注释，删除多余的代码片段，保留需要递交的代码片段。

`submit` 命令可以识别的特殊注释如下：

- `/*`_`symbols`_`SUBMIT BEGIN`_`symbols`_`*/`: 指定**需要**提交的代码的**起始**位置
- `/*`_`symbols`_`SUBMIT END`_`symbols`_`*/`: 指定**需要**提交的代码的**终止**位置
- `/*`_`symbols`_`NOT SUBMIT BEGIN`_`symbols`_`*/`: 指定**无需**提交的代码的**起始**位置
- `/*`_`symbols`_`NOT SUBMIT END`_`symbols`_`*/`: 指定**无需**提交的代码的**终止**位置

> [!NOTE]
>
> - _`symbols`_ 可以是符号 `*`, `-`, `=`, ` `(空格) 的任意组合
> - 注释不区分大小写

举例：

```sas
/*
Top-Level Comment
*/

proc datasets library = work memtype = data kill noprint;
quit;

dm ' log; clear; output; clear; odsresult; clear; ';

/*SUBMIT BEGIN*/
proc sql noprint;
    create table work.adsl as select * from rawdata.adsl;
quit;

proc sql noprint;
    create table work.t_6_1_1 as select * from adsl;
quit;
/*SUBMIT END*/

%LOG;
%ERROR;
```

经 `submit` 命令处理之后将会变成：

```sas
proc sql noprint;
    create table work.adsl as select * from rawdata.adsl;
quit;

proc sql noprint;
    create table work.t_6_1_1 as select * from adsl;
quit;
```

### 处理单个 SAS 文件

子命令 `copyfile` 用于处理单个 `.sas` 文件。

```bash
submit copyfile "adae.sas" "adae.txt"
submit cpf "adae.sas" "adae.txt"
```

其中，`adae.sas` 是需要处理的 `.sas` 文件路径，`adae.txt` 是处理后保存的 `.txt` 文件路径。

> [!TIP]
>
> - `cpf` 是 `copyfile` 的别名（_alias_），大多数选项都具有别名，可通过 `--help` 命令查看。
> - 可以使用相对路径和绝对路径，使用相对路径时，以 `submit` 命令执行所在目录为根。
>   例如：在 `/code` 目录下处理子目录 `/code/adam` 中的 `adae.sas` 文件，应该执行 `submit copyfile "adam/adae.sas" "submit/adae.txt"`，此时 `adae.txt` 文件将保存在 `/code/submit` 目录下。

#### --convert-mode

`--convert-mode` 选项用于指定处理模式，可选值为：`positive`, `negative`, `both`，默认为 `both`。

- `positive`: 仅处理 `/* SUBMIT BEGIN */`, `/* SUBMIT END */`
- `negative`: 仅处理 `/* NOT SUBMIT BEGIN*/`, `/* NOT SUBMIT END */`
- `both`: 同时处理所有四个特殊注释

> [!IMPORTANT]
>
> `/* NOT SUBMIT BEGIN*/`, `/* NOT SUBMIT END */` 的处理优先级高于 `/* SUBMIT BEGIN */`, `/* SUBMIT END */`。

```bash
submit copyfile --convert-mode negative
```

上述命令将会把：

```sas
%macro BAplot(indata, var, outdata);
    data _tmp1;
        set &indata;
    run;

    proc sql noprint;
        create table _tmp2 as select * from _tmp1;
    quit;

    data &outdata;
        set _tmp2;
    run;

    /*NOT SUBMIT BEGIN*/
    proc template;
        define statgraph BAplot;
            begingraph;
                entrytitle "BA Plot";
                layout overlay;
                    scatterplot x=Period y=BA / group=Subject;
                endlayout;
            endgraph;
        end;
    run;

    proc sgrender data=&outdata template=BAplot;
    run;
    /*NOT SUBMIT END*/
%mend BAplot;
```

处理为：

```sas
%macro BAplot(indata, var, outdata);
    data _tmp1;
        set &indata;
    run;

    proc sql noprint;
        create table _tmp2 as select * from _tmp1;
    quit;

    data &outdata;
        set _tmp2;
    run;


%mend BAplot;
```

#### --macro-subs

`--macro-subs` 选项用于替换 `.sas` 文件中宏变量，它应当是一个字典，形式为 `{key=value,...}`，其键 `key` 为宏变量名称，值 `value` 为替换字符串。

例如，如果想将下面的代码块中的宏变量 `&id` 替换为 `01`：

```sas
/*submit begin*/
data adeff;
    set adeff.adeff&id;
run;
/*submit end*/
```

你需要指定 `--macro-subs "{id=01}"`。

> [!TIP]
>
> `value` 可以为空，例如 `--macro-subs "{id=}"`，此时程序将会删除宏变量 `&id`。

> [!WARNING]
>
> `--macro-subs` 不支持嵌套的宏变量，例如：`&&id`，`&&&id` 等。

#### --encoding

`--encoding` 选项指定 `.sas` 文件的编码格式。若未指定该选项，将尝试猜测最有可能的编码格式，并用于后续处理。

```bash
submit copyfile --convert-mode negative --encoding gbk
```

> [!NOTE]
>
> 本程序使用 [chardet](https://github.com/chardet/chardet) 进行编码格式的自动识别，但 `chardet` 会将 `gbk` 编码的文件错误地识别为 `gb2312` 编码。https://github.com/chardet/chardet/issues/168
>
> 如果出现类似 `UnicodeDecodeError:'gb2312'codec can't decode byte xfb in position 6436: illegal multibyte sequence` 的错误提示，请尝试手动指定 `--encoding gbk`。

### 处理多个 SAS 文件

子命令 `copydir` 用于处理包含 `.sas` 文件的目录，该命令将以递归的方式自动查找扩展名为 `.sas` 的文件并进行处理，非 `.sas` 文件将被忽略。

```bash
submit copydir "/source" "/dest"
```

#### --convert-mode

同 [`--convert-mode`](#--convert-mode)

#### --macro-subs

同 [`--macro-subs`](#--macro-subs)

#### --encoding

同 [`--encoding`](#--encoding)

#### --merge

`--merge` 选项指定将所有 `.sas` 文件进行转换后合并到单个 `.txt` 文件。

例如：

```bash
submit copydir "/source" "/dest" --merge "code.txt"
```

上述代码会将 `/source` 目录中的所有 `.sas` 文件转换成 `.txt` 文件，并将转换后的 `.txt` 文件合并到 `/dest/code.txt` 中。

> [!NOTE]
>
> 合并后的 `.txt` 文件包含源目录中所有需要递交的 sas 代码，使用注释 `/*======`_`filename`_`.txt======*/` 分隔来自不同 `.sas` 文件的代码。
> 其中 _`filename`_ 是源目录中 `.sas` 文件名称（不含扩展名）。

> [!IMPORTANT]
>
> 某些地方医疗器械监督管理局不接收压缩包作为递交文件，且递交文件数量存在限制，因此必须将所有 `.sas` 文件合并成一个单独的 `.txt` 文件。

#### --exclude-dirs

`--exclude-dirs` 选项指定排除的目录列表，这些目录中的文件将会被跳过处理。

```bash
submit copydir "/source" "/dest" --exclude-dirs macro
```

可同时指定多个目录：

```bash
submit copydir "/source" "/dest" --exclude-dirs macro qc initial
```

上述命令将在目录名称匹配 `macro`, `qc` 或 `initial` 时跳过处理其中的文件。

#### --exclude-files

`--exclude-files` 选项指定排除的文件列表，这些文件将会被跳过处理。

```bash
submit copydir "/source" "/dest" --exclude-dirs macro --exclude-files fcmp.sas format.sas
```

上述命令将在目录名称匹配 `macro` 时跳过处理其中的文件，并在文件名称匹配 `fcmp.sas` 或 `format.sas` （无论是否在 `macro` 目录中）时跳过处理。

### 命令行选项参考

#### submit copyfile

```bash
usage: submit [options] copyfile [-h] [-c {positive,negative,both}] [--macro-subs MACRO_SUBS] [--encoding ENCODING] sas_file txt_file

positional arguments:
  sas_file              SAS 文件路径
  txt_file              TXT 文件路径

options:
  -h, --help            show this help message and exit
  -c, --convert-mode {positive,negative,both}
                        转换模式（默认 both）
  --macro-subs MACRO_SUBS
                        宏变量替换，格式为 {key=value,...}（默认无）
  --encoding ENCODING   编码格式（默认自动检测）
```

#### submit copydir

```bash
usage: submit [options] copydir [-h] [-c {positive,negative,both}] [--macro-subs MACRO_SUBS] [--encoding ENCODING] [-mrg MERGE] [-exf [EXCLUDE_FILES ...]] [-exd [EXCLUDE_DIRS ...]] sas_dir txt_dir

positional arguments:
  sas_dir               SAS 文件目录
  txt_dir               TXT 文件目录

options:
  -h, --help            show this help message and exit
  -c, --convert-mode {positive,negative,both}
                        转换模式（默认 both）
  --macro-subs MACRO_SUBS
                        宏变量替换，格式为 {key=value,...}（默认无）
  --encoding ENCODING   编码格式（默认自动检测）
  -mrg, --merge MERGE   合并到一个文件（默认无）
  -exf, --exclude-files [EXCLUDE_FILES ...]
                        排除文件列表（默认无）
  -exd, --exclude-dirs [EXCLUDE_DIRS ...]
                        排除目录列表（默认无）
```

### bat 脚本编写示例

`.bat` 文件是一种[批处理文件](https://en.wikipedia.org/wiki/Batch_file)，你可以将多条 `submit` 命令保存在单个 `.bat` 文件中，这样只需双击这个文件即可批量处理 `.sas` 文件。

例如：

```bash
submit copydir "D:/project/code/adam" "D:/project/submit/adam"
submit copydir "D:/project/code/tfl" "D:/project/submit/tfl" --exclude-files merge.sas
submit copydir "D:/project/code/macro" "D:/project/submit/macro" --convert-mode negative
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
   uv sync
   ```

3. 安装 pre-commit

   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

4. 修改代码

5. 测试代码

   ```bash
   pytest
   ```

> [!NOTE]
>
> 执行 `pytest` 命令前需要先激活虚拟环境。

6. 发起 pull request

> [!NOTE]
>
> 1. 推荐使用 [VSCode](https://code.visualstudio.com/Download) 编辑代码
> 2. 需要使用 [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) 规范的提交信息
