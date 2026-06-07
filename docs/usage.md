# Command Line Interface Reference

- `copyfile`

  裁剪单个 sas 文件，保存处理后的代码到 txt 文件中。
  
  具体选项详见 [`copyfile`](#copyfile)

  ```bash
  submit copyfile ...
  ```

- `copydir`

  以递归的方式裁剪指定目录下的所有 sas 文件，保存处理后的代码到指定目录中。
  
  具体选项详见 [`copydir`](#copydir)

  ```bash
  submit copydir ...
  ```

- `--help`, _optional_

  显示帮助信息并退出。

  ```bash
  submit --help
  ```

## `copyfile`

- `-s, -sas-file`, _required_

  指定需裁剪的 `.sas` 文件路径。
  
  可以使用绝对路径和相对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

- `-t, -txt-file`, _required_

  指定裁剪后的代码保存的 `.txt` 文件路径。
  
  可以使用绝对路径和相对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

- `--positive/--no-positive`, _optional_ <span id="--positive/--no-positive"></span>

  指定是否处理 _positive_ 模式的注释，如未指定，默认使用 `--positive`。

  ```bash
  submit copyfile -s "./adam/adae.sas" -t "./output/adae.txt" --no-positive
  ```

- `--negative/--no-negative`, _optional_ <span id="--negative/--no-negative"></span>

  指定是否处理 _negative_ 模式的注释，如未指定，默认使用 `--negative`。

  📌 `--negative` 优先级高于 `--positive`，这意味着如果同时指定了 `--positive` 和 `--negative`，程序会优先处理 _negative_ 模式的注释。

  ```bash
  submit copyfile -s "./adam/adae.sas" -t "./output/adae.txt" --no-positive --no-negative
  ```

- `-sub, --substitute`, _optional_ <span id="--substitute"></span>

  指定需替换的宏变量和宏变量的值，格式为 _`name`_ _`value`_。

  例如：需要将代码中的宏变量 `&id` 替换为 `%str()`，可以指定 `--substitute "id" "%str()"`，程序只会将宏变量 `&id` 替换成 `%str()`，不会处理嵌套的宏变量（如：`&&id`, `&&&id`, ...）。

  该选项可以多次使用，指定多个替换项。

  ```bash
  submit copyfile -s "./adam/adae.sas" -t "./output/adae.txt" --substitute "id" "%str()"
  ```

- `-e, --encoding`, _optional_ <span id="--encoding"></span>

  指定 `.sas` 文件的字符编码，默认值为 `gbk`。

  ```bash
  submit copyfile -s "./adam/adae.sas" -t "./output/adae.txt" --encoding "utf-8"
  ```

- `--help`, _optional_

  显示帮助信息并退出。

  ```bash
  submit copyfile --help
  ```

## `copydir`

- `-s, --sas-dir`, _required_

  指定包含需裁剪的 sas 代码的目录路径。
  
  可以使用绝对路径和相对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

- `-t, --txt-dir`, _required_

  指定裁剪后的 sas 代码保存的目录路径。
  
  可以使用绝对路径和相对路径，使用相对路径时，以执行 `submit` 命令的终端的当前目录为根。

- `--positive/--no-positive`, _optional_

  同 [`--positive/--no-positive`](#--positive/--no-positive)

  ```bash
  submit copydir -s "./adam" -t "./output" --no-positive
  ```

- `--negative/--no-negative`, _optional_

  同 [`--negative/--no-negative`](#--negative/--no-negative)

  ```bash
  submit copydir -s "./adam" -t "./output" --no-positive --no-negative
  ```

- `-sub, --substitute`, _optional_

  同 [`-sub, --substitute`](#--substitute)

  ```bash
  submit copydir -s "./adam" -t "./output" --substitute "id" "%str()"
  ```

- `-e, --encoding`, _optional_

  同 [`-e, --encoding`](#--encoding)

  ```bash
  submit copydir -s "./adam" -t "./output" --encoding "utf-8"
  ```

- `--merge`, _optional_

  指定是否将所有处理后的代码合并到一个文件中。

> [!NOTE]
>
> 合并后的 `.txt` 文件包含源目录中所有未被 `--exclude-dir` 和 `--exclude-file` 排除的 sas 代码。
>
> 使用注释 `/*====================`_`filename`_`.sas====================*/` 分隔来自不同文件的代码。
> 其中 _`filename`_ 是源目录中 `.sas` 文件的名称。

> [!IMPORTANT]
>
> 某些地方医疗器械监督管理局不接收压缩包作为递交文件，且递交文件数量存在限制，
> 因此必须将所有 `.sas` 文件合并成一个单独的 `.txt` 文件。

```bash
submit copydir -s "./adam" -t "./output" --substitute "id" "%str()" --merge
```

- `--merge-name`, _optional_

  指定合并后的文件名，默认值为 `merged.txt`，仅当指定了 `--merge` 选项时有效。

  ```bash
  submit copydir -s "./adam" -t "./output" --substitute "id" "%str()" --merge --merge-name "adam.txt"
  ```

- `-exd, --exclude-dir`, _optional_

  指定需排除的目录的 [glob 路径模式](#glob-模式介绍)，所有匹配该模式的目录中的 `.sas` 文件将被忽略。

  该选项可以多次使用，指定多个排除目录。

  ```bash
  submit copydir -s "./adam" -t "./output" --exclude-dir "sponser-only"
  ```

- `-exf, --exclude-file`, _optional_

  指定需排除的文件的 [glob 路径模式](#glob-模式介绍)，所有匹配该模式的文件将被忽略。

  ```bash
  submit copydir -s "./adam" -t "./output" --exclude-file "**/deprecated*.sas"
  ```

  该选项可以多次使用，指定多个排除文件。

- `--help`, _optional_

  显示帮助信息并退出。

  ```bash
  submit copydir --help
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
