# 选项参考

## 子命令 `copyfile`

子命令 `copyfile` 用于处理单个 `.sas` 文件，可用的选项如下：

### `-s, -sas-file`

指定需裁剪的 `.sas` 文件路径，可以使用相对路径和绝对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

### `-t, -txt-file`

指定处理后的代码保存的 `.txt` 文件路径，可以使用相对路径和绝对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

### `--positive`

指定处理 _positive_ 模式的注释。

### `--no-positive`

指定不要处理 _positive_ 模式的注释。

### `--negative`

指定处理 _negative_ 模式的注释，优先级高于 `--positive`。

### `--no-negative`

指定不要处理 _negative_ 模式的注释。

### `-sub, --substitute`

指定需替换的宏变量和宏变量的值，该选项可以多次使用，表示多个替换项。

### `-e, --encoding`

指定 `.sas` 文件的字符编码，默认值为 `gbk`。

### `--help`

显示帮助信息并退出。

### 示例

```bash
submit copyfile -s "./adae.sas" "./output/adae.txt"
submit copyfile -s "./adae.sas" "./output/adae.txt" --no-negative
submit copyfile -s "./adae.sas" "./output/adae.txt" --no-negative --substitute "id" "%str()" --substitute "indata" "adeff"
submit copyfile -s "./adae.sas" "./output/adae.txt" --no-negative --encoding utf-8
```

## 子命令 `copydir`

子命令 `copydir` 用于处理包含 `.sas` 文件的目录，该命令将以递归的方式自动查找扩展名为 `.sas` 的文件并进行处理，非 `.sas` 文件将被忽略。

可用的选项如下：

### `-s, --sas-dir`

指定包含需裁剪的 sas 代码的目录路径，可以使用相对路径和绝对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

### `-t, --txt-dir`

指定裁剪后的 sas 代码保存的目录路径，可以使用相对路径和绝对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

### `--positive`

同 [--positive](#--positive)

### `--no-positive`

同 [--no-positive](#--no-positive)

### `--negative`

同 [--negative](#--negative)

### `--no-negative`

同 [--no-negative](#--no-negative)

### `-sub, --substitute`

同 [--substitute](#-sub---substitute)

### `-e, --encoding`

同 [`--encoding`](#--encoding)

### `--merge`

指定是否将所有处理后的代码合并到一个文件中。

> [!NOTE]
>
> 合并后的 `.txt` 文件包含源目录中所有需要递交的 sas 代码，使用注释 `/*====================`_`filename`_`.sas====================*/` 分隔来自不同 `.sas` 文件的代码。
> 其中 _`filename`_ 是源目录中 `.sas` 文件名称。

> [!IMPORTANT]
>
> 某些地方医疗器械监督管理局不接收压缩包作为递交文件，且递交文件数量存在限制，因此必须将所有 `.sas` 文件合并成一个单独的 `.txt` 文件。

### `--merge-name`

指定合并后的文件名，默认值为 `merged.txt`，仅当指定了 `--merge` 选项时有效。

### `-exd, --exclude-dir`

指定需排除的目录的 [glob 路径模式](#glob-模式介绍)，所有匹配该模式的目录中的 `.sas` 文件将被忽略。

该选项可以多次使用，表示多个排除目录。

### `-exf, --exclude-file`

指定需排除的文件的 [glob 路径模式](#glob-模式介绍)，所有匹配该模式的文件将被忽略。

该选项可以多次使用，表示多个排除文件。

### 示例

```bash
submit copydir "./adam" "./adam/output"
submit copydir "./adam" "./adam/output" --exclude-file "**/deprecated*.sas"
submit copydir "./adam" "./adam/output" --exclude-file "**/deprecated*.sas" --exclude-dir "sponser-only" --exclude-dir "test-only"
submit copydir "./adam" "./adam/output" --merge --merge-name "all.txt"
```

## glob 模式介绍

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
