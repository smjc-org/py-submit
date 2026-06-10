# author: @Snoopy1866

import re

from dataclasses import dataclass
from pathlib import Path

import click

from natsort import index_natsorted

SYLBOMS = r"[\s\*\-\=]"

# 需要递交的代码片段的开始和结束标记 (positive mode)
# /*SUBMIT BEGIN*/ 和 /*SUBMIT END*/ 之间的代码将被保留
POSITIVE_COMMENT_BEGIN = rf"\/\*{SYLBOMS}*SUBMIT\s*BEGIN{SYLBOMS}*\*\/"
POSITIVE_COMMENT_END = rf"\/\*{SYLBOMS}*SUBMIT\s*END{SYLBOMS}*\*\/"


# 不要递交的代码片段的开始和结束标记 (negative mode)
# /*NOT SUBMIT BEGIN*/ 和 /*NOT SUBMIT END*/ 之间的代码将移除
NEGATIVE_COMMENT_BEGIN = rf"\/\*{SYLBOMS}*NOT\s*SUBMIT\s*BEGIN{SYLBOMS}*\*\/"
NEGATIVE_COMMENT_END = rf"\/\*{SYLBOMS}*NOT\s*SUBMIT\s*END{SYLBOMS}*\*\/"


@dataclass
class CopyFileTask:
    sas_file: Path
    txt_file: Path
    positive: bool
    negative: bool
    substitute: dict[str, str]
    encoding: str


def _cut_code(
    file: Path,
    positive: bool = True,
    negative: bool = True,
    substitute: dict[str, str] = {},
    encoding: str = "gbk",
) -> None:
    """裁剪代码。

    Args:
        file (Path): 代码文件路径。
        positive (bool): 是否处理 positive 模式的注释。
        negative (bool): 是否处理 negative 模式的注释，优先级高于 `positive`。
        encoding (str, optional): 字符编码。
        substitute (dict[str, str], optional): 宏变量替换字典。
    """

    re_flags = re.I | re.S

    code = file.read_text(encoding=encoding)

    # 处理特殊注释，NEGATIVE 模式处理优先级高于 POSITIVE 模式
    if negative:
        start_match = re.search(rf"{NEGATIVE_COMMENT_BEGIN}", code, flags=re_flags)
        end_match = re.search(rf"{NEGATIVE_COMMENT_END}", code, flags=re_flags)
        if start_match and end_match:
            code = re.sub(rf"{NEGATIVE_COMMENT_BEGIN}.*?{NEGATIVE_COMMENT_END}", "", code, flags=re_flags)
        elif start_match is not None and end_match is None:
            click.secho(f"警告：源文件 {file.absolute()} 中存在 NEGATIVE 模式的起始注释，但未找到对应的终止注释！", fg="yellow", err=True)
        elif start_match is None and end_match is not None:
            click.secho(f"警告：源文件 {file.absolute()} 中存在 NEGATIVE 模式的终止注释，但未找到对应的起始注释！", fg="yellow", err=True)
        else:
            pass

    if positive:
        start_match = re.search(rf"{POSITIVE_COMMENT_BEGIN}", code, flags=re_flags)
        end_match = re.search(rf"{POSITIVE_COMMENT_END}", code, flags=re_flags)
        if start_match and end_match:
            code_segaments = re.findall(rf"{POSITIVE_COMMENT_BEGIN}(.*?){POSITIVE_COMMENT_END}", code, re_flags)
            code = "\n\n".join(code.strip() for code in code_segaments)
        elif start_match is not None and end_match is None:
            click.secho(f"警告：源文件 {file.absolute()} 中存在 POSITIVE 模式的起始注释，但未找到对应的终止注释！", fg="yellow", err=True)
        elif start_match is None and end_match is not None:
            click.secho(f"警告：源文件 {file.absolute()} 中存在 POSITIVE 模式的终止注释，但未找到对应的起始注释！", fg="yellow", err=True)
        else:
            click.secho(f"警告：源文件 {file.absolute()} 中未找到预期的 POSITIVE 模式的注释，将不裁剪任何代码！", fg="yellow", err=True)

    # 替换宏变量
    if substitute:
        for macro, value in substitute.items():
            code = re.sub(rf"(?<!&)&{macro}(?![A-Za-z_])", value, code, flags=re_flags)

    return code.strip()


def _copy_file(sas_file: Path, txt_file: Path, positive: bool, negative: bool, substitute: dict[str, str], encoding: str) -> None:
    """处理单个 sas 文件，保存处理后的代码到 txt 文件中。"""

    code = _cut_code(sas_file, positive, negative, substitute, encoding)

    txt_file_dir = txt_file.parent
    if not txt_file_dir.exists():
        txt_file_dir.mkdir(parents=True)
    txt_file.write_text(code, encoding=encoding)


@click.group()
def cli() -> None:
    """sas 代码裁剪工具"""
    pass


@cli.command(name="copyfile", help="处理单个 sas 文件，保存处理后的代码到 txt 文件中。")
@click.option(
    "-s",
    "--sas-file",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, path_type=Path),
    help="包含需裁剪的 sas 代码的文件路径",
)
@click.option(
    "-t",
    "--txt-file",
    required=True,
    type=click.Path(resolve_path=True, writable=True, path_type=Path),
    help="裁剪后的 sas 代码保存的文件路径",
)
@click.option("--positive/--no-positive", is_flag=True, default=True, help="是否处理 positive 模式的注释")
@click.option("--negative/--no-negative", is_flag=True, default=True, help="是否处理 negative 模式的注释，优先级高于 --positive")
@click.option("-sub", "--substitute", multiple=True, type=(str, str), default=(), help="宏变量替换键值对")
@click.option("-e", "--encoding", default="gbk", type=str, help="字符编码，默认值为 gbk")
def copy_file(
    sas_file: Path,
    txt_file: Path,
    positive: bool,
    negative: bool,
    substitute: tuple[tuple[str, str], ...],
    encoding: str,
) -> None:
    """处理单个 sas 文件，保存处理后的代码到 txt 文件中。"""

    if substitute:
        substitute = dict(substitute)
    _copy_file(sas_file, txt_file, positive, negative, substitute, encoding)


@cli.command(name="copydir", help="处理指定目录下的所有 sas 文件，保存处理后的代码到指定目录中。")
@click.option(
    "-s",
    "--sas-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, path_type=Path),
    help="包含需裁剪的 sas 代码的目录路径",
)
@click.option(
    "-t",
    "--txt-dir",
    required=True,
    type=click.Path(resolve_path=True, path_type=Path),
    help="裁剪后的 sas 代码保存的目录路径",
)
@click.option("--positive/--no-positive", is_flag=True, default=True, help="是否处理 positive 模式的注释")
@click.option("--negative/--no-negative", is_flag=True, default=True, help="是否处理 negative 模式的注释，优先级高于 --positive")
@click.option("-sub", "--substitute", multiple=True, type=(str, str), default=(), help="宏变量替换键值对")
@click.option("-e", "--encoding", default="gbk", type=str, help="字符编码，默认值为 gbk")
@click.option("--merge/--no-merge", is_flag=True, help="是否将所有处理后的代码合并到一个文件中")
@click.option("--merge-name", default="merged.txt", type=str, help="合并后的文件名，默认值为 merged.txt，仅当指定了 --merge 选项时有效")
@click.option("-exd", "--exclude-dir", multiple=True, type=str, help="排除的目录路径模式")
@click.option("-exf", "--exclude-file", multiple=True, type=str, help="排除的文件路径模式")
def copy_directory(
    sas_dir: Path,
    txt_dir: Path,
    positive: bool = True,
    negative: bool = True,
    substitute: tuple[tuple[str, str], ...] = ((),),
    encoding: str = "gbk",
    merge: bool = False,
    merge_name: str = "merged.txt",
    exclude_dir: tuple[str, ...] = (),
    exclude_file: tuple[str, ...] = (),
) -> None:
    """处理指定目录下的所有 sas 文件，保存处理后的代码到指定目录中。

    Args:
        sas_dir (Path): 包含 sas 文件的目录路径。
        txt_dir (Path): 存储 txt 文件的目录路径。
        positive (bool): 是否处理 positive 模式的注释。
        negative (bool): 是否处理 negative 模式的注释，优先级高于 `positive`。
        substitute (tuple[tuple[str, str], ...]): 宏变量替换键值对。
        encoding (str): 字符编码。
        merge (bool): 是否将所有处理后的代码合并到一个文件中。
        merge_name (str): 合并后的文件名，默认值为 `'merged.txt'`，仅当 `merge` 选项为 True 时有效。
        exclude_file (tuple[Path, ...]): 排除的文件路径。
        exclude_dir (tuple[Path, ...]): 排除的目录路径。
    """

    if substitute:
        substitute = dict(substitute)

    resolved_exclude_dirs: set[Path] = set()
    resolved_exclude_files: set[Path] = set()

    if not txt_dir.exists():
        txt_dir.mkdir(parents=True)

    if exclude_dir:
        for pattern in exclude_dir:
            resolved_exclude_dirs.update(sas_dir.glob(pattern))

    if exclude_file:
        for pattern in exclude_file:
            resolved_exclude_files.update(sas_dir.glob(pattern))

    # 记录需要处理的 sas 文件
    copy_file_tasks: list[CopyFileTask] = []

    # 处理 SAS 文件
    for dirpath, _, filenames in sas_dir.walk():
        if resolved_exclude_dirs and dirpath in resolved_exclude_dirs:
            click.secho(f"已排除目录：{dirpath.absolute()}", fg="magenta")
            continue
        if txt_dir in dirpath.parents:  # 如果当前目录在指定输出 TXT 的目录内，则跳过
            click.secho(f"已跳过目录：{dirpath.absolute()}，跳过原因：当前目录在指定输出 TXT 的目录内", fg="magenta")
            continue
        if dirpath == txt_dir:  # 如果当前目录与指定输出 TXT 的目录是同一目录，则跳过
            click.secho(f"已跳过目录：{dirpath.absolute()}，跳过原因：当前目录与指定输出 TXT 的目录是同一目录", fg="magenta")
            continue
        for file in filenames:
            fileabspath = dirpath / file
            if resolved_exclude_files and fileabspath in resolved_exclude_files:
                click.secho(f"已排除文件：{fileabspath.absolute()}", fg="magenta")
                continue
            if file.endswith(".sas"):
                dirrelpath = dirpath.relative_to(sas_dir)
                txt_file = txt_dir / dirrelpath / file.replace(".sas", ".txt")
                copy_file_tasks.append(
                    CopyFileTask(
                        sas_file=fileabspath, txt_file=txt_file, positive=positive, negative=negative, substitute=substitute, encoding=encoding
                    )
                )

    if not copy_file_tasks:
        click.secho("未找到需要处理的 .sas 文件", fg="yellow")
        return

    if merge:  # 合并文件
        merge_file = txt_dir / merge_name

        # 对任务按照 txt_file.name 进行自然排序
        txt_file_names = [task.txt_file.name for task in copy_file_tasks]
        index = index_natsorted(txt_file_names)
        sorted_copy_file_tasks = [copy_file_tasks[i] for i in index]

        # 写入 merge_file
        with open(merge_file, "w", encoding=encoding) as f:
            for task in sorted_copy_file_tasks:
                f.write(f"/*===================={task.sas_file.name}====================*/\n\n")

                code_content = _cut_code(task.sas_file, task.positive, task.negative, task.substitute, task.encoding)
                f.write(code_content)

                f.write("\n\n\n")
                click.secho(f"已转换文件：{task.sas_file.absolute()}", fg="green")
        click.secho(f"已生成文件：{merge_file.absolute()}", fg="green")
    else:  # 不合并文件
        for task in copy_file_tasks:
            _copy_file(task.sas_file, task.txt_file, task.positive, task.negative, task.substitute, task.encoding)
            click.secho(f"已转换文件：{task.sas_file.absolute()}", fg="green")
