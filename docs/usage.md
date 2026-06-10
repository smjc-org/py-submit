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

> [!NOTE]
>
> 指定 `--positive` 时，若文件不包含 _positive_ 模式的注释，程序会发出警告，不进行裁剪处理。

- `--negative/--no-negative`, _optional_ <span id="--negative/--no-negative"></span>

  指定是否处理 _negative_ 模式的注释，如未指定，默认使用 `--negative`。

  ```bash
  submit copyfile -s "./adam/adae.sas" -t "./output/adae.txt" --no-positive --no-negative
  ```


> [!NOTE]
>
> `--negative` 优先级高于 `--positive`，如果同时指定 `--positive` 和 `--negative`，程序会优先处理 _negative_ 模式的注释。
>
> 举例来说，假设文件 `adsl.sas` 的内容如下：
> ```sas
> %let syscc = 0;
>
> dm log 'clear';
> dm output 'clear';
> dm odsresult 'clear';
>
> proc datasets lib=work kill memtype=data nolist;
> quit;
>
> /* SUBMIT BEGIN */
> proc sql noprint;
>     create table adsl as
>         select ...
> quit;
>
> /* NOT SUBMIT BEGIN */
> proc means data = adsl;
>     var age;
> run;
> /* NOT SUBMIT END */
>
> proc sort data = adsl;
>     by usubjid;
> run;
> /* SUBMIT END */
>
> %sm_log;
> %error;
> ```
>
> 运行以下命令：
>
> ```bash
> submit copyfile -s "./adsl.sas" -t "./adsl.txt" --positive --negative
> ```
>
> `adsl.txt` 的内容如下：
>
> ```txt
> proc sql noprint;
>     create table adsl as
>         select ...
> quit;
>
>
>
> proc sort data = adsl;
>     by usubjid;
> run;
> ```txt

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

  指定裁剪后的 sas 代码保存的目录路径，目录不存在时将自动创建。
  
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

  ```bash
  submit copydir -s "./adam" -t "./output" --substitute "id" "%str()" --merge
  ```

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

- `--merge-name`, _optional_

  指定合并后的文件名，默认值为 `merged.txt`，仅当指定了 `--merge` 选项时有效。

  ```bash
  submit copydir -s "./adam" -t "./output" --substitute "id" "%str()" --merge --merge-name "adam.txt"
  ```

- `-exd, --exclude-dir`, _optional_

  指定需排除的目录的 [glob 模式](https://docs.python.org/zh-cn/3/library/pathlib.html#pattern-language)，所有匹配该模式的目录中的 `.sas` 文件将被忽略。

  该选项可以多次使用，指定多个排除目录。

  ```bash
  submit copydir -s "./adam" -t "./output" --exclude-dir "sponser-only"
  ```

- `-exf, --exclude-file`, _optional_

  指定需排除的文件的 [glob 模式](https://docs.python.org/zh-cn/3/library/pathlib.html#pattern-language)，所有匹配该模式的文件将被忽略。

  ```bash
  submit copydir -s "./adam" -t "./output" --exclude-file "**/deprecated*.sas"
  ```

  该选项可以多次使用，指定多个排除文件。

- `--help`, _optional_

  显示帮助信息并退出。

  ```bash
  submit copydir --help
  ```
