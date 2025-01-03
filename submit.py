# author: @Snoopy1866

from __future__ import annotations
import argparse
import glob
import os
import re
from enum import IntFlag, auto

from chardet import detect
from natsort import natsorted

SYLBOMS = r"[\s\*\-\=]"

# 需要递交的代码片段的开始和结束标记
# /*SUBMIT BEGIN*/ 和 /*SUBMIT END*/ 之间的代码将被递交
COMMENT_SUBMIT_BEGIN = rf"\/\*{SYLBOMS}*SUBMIT\s*BEGIN{SYLBOMS}*\*\/"
COMMENT_SUBMIT_END = rf"\/\*{SYLBOMS}*SUBMIT\s*END{SYLBOMS}*\*\/"


# 不要递交的代码片段的开始和结束标记
# /*NOT SUBMIT BEGIN*/ 和 /*NOT SUBMIT END*/ 之间的代码将不会被递交
# /*NOT SUBMIT BEGIN*/ 和 /*NOT SUBMIT END*/ 的优先级高于 /*SUBMIT BEGIN*/ 和 /*SUBMIT END*/
COMMENT_NOT_SUBMIT_NEGIN: str = rf"\/\*{SYLBOMS}*NOT\s*SUBMIT\s*BEGIN{SYLBOMS}*\*\/"
COMMENT_NOT_SUBMIT_END: str = rf"\/\*{SYLBOMS}*NOT\s*SUBMIT\s*END{SYLBOMS}*\*\/"

# 宏变量
# 仅支持一层宏变量引用（例如：&id），不支持嵌套宏变量引用（例如：&&id、&&&id）
MACRO_VAR = r"(?<!&)(&[A-Za-z_][A-Za-z0_9_]*)"


class ConvertMode(IntFlag):
    """转换模式。"""

    # 仅考虑需要递交的代码片段
    POSITIVE = auto()

    # 仅考虑不需要递交的代码片段
    NEGATIVE = auto()

    # 同时考虑需要递交的代码片段和不需要递交的代码片段
    BOTH = POSITIVE | NEGATIVE

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def get_from_str(cls, value: str) -> ConvertMode:
        try:
            return cls[value.upper()]
        except KeyError:
            raise argparse.ArgumentTypeError(f"无效的转换模式：{value}")

    @classmethod
    def get_available_values(cls) -> list[ConvertMode]:
        modes = [mode for mode in cls]
        modes.append(ConvertMode.BOTH)
        return modes


def expand_glob_patterns(patterns: list[str], root_dir: str) -> list[str]:
    """扩展 glob 模式。

    Args:
        patterns (list[str]): glob 模式列表。
        root_dir (str): 根目录。

    Returns:
        list[str]: 文件路径列表。
    """
    path = []
    for pattern in patterns:
        path.extend(glob.glob(pattern, root_dir=root_dir, recursive=True))
    return path


def copy_file(
    sas_file: str,
    txt_file: str,
    convert_mode: ConvertMode = ConvertMode.BOTH,
    macro_subs: dict[str, str] | None = None,
    encoding: str | None = None,
) -> None:
    """将 SAS 代码复制到 txt 文件中，并移除指定标记之间的内容。

    Args:
        sas_file (str): SAS 文件路径。
        txt_file (str): TXT 文件路径。
        convert_mode (ConvertMode, optional): 转换模式，默认值为 ConvertMode.BOTH。
        macro_subs (dict[str, str] | None, optional): 一个字典，其键为 SAS 代码中的宏变量名称，值为替代的字符串，默认值为 None。
        encoding (str | None, optional): 字符编码，默认值为 None，将自动检测编码。
    """

    if encoding is None:
        with open(sas_file, "rb") as f:
            encoding = detect(f.read())["encoding"]

    with open(sas_file, "r", encoding=encoding) as f:
        code = f.read()

    # 提取代码片段
    if convert_mode & ConvertMode.NEGATIVE:
        # 移除不需要递交的代码片段
        code = re.sub(rf"{COMMENT_NOT_SUBMIT_NEGIN}.*?{COMMENT_NOT_SUBMIT_END}", "", code, flags=re.I | re.S)

    if convert_mode & ConvertMode.POSITIVE:
        # 提取需要递交的代码片段
        code = re.findall(rf"{COMMENT_SUBMIT_BEGIN}(.*?){COMMENT_SUBMIT_END}", code, re.I | re.S)
        code = "".join(code)

    # 替换宏变量
    if macro_subs is not None:
        for key, value in macro_subs.items():
            regex_macro = re.compile(rf"(?<!&)&{key}")
            code = re.sub(regex_macro, value, code)

    txt_file_dir = os.path.dirname(txt_file)
    if not os.path.exists(txt_file_dir):
        os.makedirs(txt_file_dir)
    with open(txt_file, "w", encoding=encoding) as f:
        f.write(code)


def copy_directory(
    sas_dir: str,
    txt_dir: str,
    merge: str | None = None,
    convert_mode: ConvertMode = ConvertMode.BOTH,
    macro_subs: dict[str, str] | None = None,
    exclude_files: list[str] = None,
    exclude_dirs: list[str] = None,
    encoding: str | None = None,
) -> None:
    """将 SAS 代码复制到 txt 文件中，并移除指定标记之间的内容。

    Args:
        sas_dir (str): SAS 文件夹路径。
        txt_dir (str): TXT 文件夹路径。
        merge (str | None, optional): 合并到一个文件，默认值为 None。
        convert_mode (ConvertMode, optional): 转换模式，默认值为 ConvertMode.BOTH。
        macro_subs (dict[str, str] | None, optional): 一个字典，其键为 SAS 代码中的宏变量名称，值为替代的字符串，默认值为 None。
        exclude_files (list[str], optional): 排除文件列表，默认值为 None。
        exclude_dirs (list[str], optional): 排除目录列表，默认值为 None。
        encoding (str | None, optional): 字符编码，默认值为 None，将自动检测编码。
    """

    if not os.path.exists(sas_dir):
        print(f"源文件夹 {sas_dir} 不存在。")
        return
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)

    if exclude_dirs:
        exclude_dirs = expand_glob_patterns(exclude_dirs, root_dir=sas_dir)

    if exclude_files:
        exclude_files = expand_glob_patterns(exclude_files, root_dir=sas_dir)

    # 转换 SAS 文件
    for dirpath, _, filenames in os.walk(sas_dir):
        dirrelpath = os.path.relpath(dirpath, sas_dir)
        if exclude_dirs is not None and dirrelpath in exclude_dirs:
            continue
        if os.path.commonpath([dirpath, sas_dir]) == txt_dir:  # 如果当前目录是目标目录或其子目录，则跳过
            continue
        for file in filenames:
            filerelpath = os.path.join(dirrelpath, file)
            if exclude_files is not None and filerelpath in exclude_files:
                continue
            if file.endswith(".sas"):
                sas_file = os.path.join(dirpath, file)
                txt_file = os.path.join(txt_dir, os.path.join(txt_dir, dirrelpath), file.replace(".sas", ".txt"))
                copy_file(sas_file, txt_file, convert_mode=convert_mode, macro_subs=macro_subs, encoding=encoding)

    # 合并文件
    if merge is not None:
        merge_file = os.path.join(txt_dir, merge)
        with open(merge_file, "w", encoding=encoding) as f:
            for dirpath, _, filenames in os.walk(txt_dir):
                filenames = natsorted(filenames)
                for file in filenames:
                    if file.endswith(".txt") and file != merge:
                        txt_file = os.path.join(dirpath, file)
                        with open(txt_file, "r", encoding=encoding) as txt:
                            f.write(f"/*======{file}======*/\n")
                            f.write(txt.read())
                            f.write("\n")

        for dirpath, _, filenames in os.walk(txt_dir):
            filenames = natsorted(filenames)
            for file in filenames:
                if file.endswith(".txt") and file != merge:
                    txt_file = os.path.join(dirpath, file)
                    os.remove(txt_file)


def parse_dict(arg: str) -> dict[str, str]:
    """解析字典字符串。

    Args:
        arg (str): 字典字符串。

    Returns:
        dict[str, str]: 字典。
    """

    arg = arg.strip("{}")
    try:
        return dict([ele.strip("\"'") for ele in item.split("=")] for item in arg.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("无效的字典字符串")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="submit",
        usage="%(prog)s [options]",
        description="本工具用于在代码递交之前进行简单的转换。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="help", default=argparse.SUPPRESS, help="显示帮助信息，例如: submit copyfile --help"
    )
    subparsers = parser.add_subparsers(dest="command")

    # 公共参数
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-c",
        "--convert-mode",
        type=ConvertMode.get_from_str,
        choices=ConvertMode.get_available_values(),
        default="both",
        help="转换模式（默认 both）",
    )
    parent_parser.add_argument("--macro-subs", type=parse_dict, help="宏变量替换，格式为 {key=value,...}（默认无）")
    parent_parser.add_argument("--encoding", default=None, help="编码格式（默认自动检测）")

    # 子命令 copyfile
    parser_file = subparsers.add_parser("copyfile", aliases=["cpf"], parents=[parent_parser], help="单个 SAS 文件转换")
    parser_file.add_argument("sas_file", help="SAS 文件路径")
    parser_file.add_argument("txt_file", help="TXT 文件路径")

    # 子命令 copydir
    parser_dir = subparsers.add_parser("copydir", aliases=["cpd"], parents=[parent_parser], help="多个 SAS 文件转换")
    parser_dir.add_argument("sas_dir", help="SAS 文件目录")
    parser_dir.add_argument("txt_dir", help="TXT 文件目录")
    parser_dir.add_argument("-mrg", "--merge", default=None, help="合并到一个文件（默认无）")
    parser_dir.add_argument("-exf", "--exclude-files", nargs="*", default=None, help="排除文件列表（默认无）")
    parser_dir.add_argument("-exd", "--exclude-dirs", nargs="*", default=None, help="排除目录列表（默认无）")

    args = parser.parse_args()

    if args.command == "copyfile":
        copy_file(
            sas_file=args.sas_file,
            txt_file=args.txt_file,
            convert_mode=args.convert_mode,
            macro_subs=args.macro_subs,
            encoding=args.encoding,
        )
    elif args.command == "copydir":
        copy_directory(
            sas_dir=args.sas_dir,
            txt_dir=args.txt_dir,
            merge=args.merge,
            convert_mode=args.convert_mode,
            macro_subs=args.macro_subs,
            exclude_files=args.exclude_files,
            exclude_dirs=args.exclude_dirs,
            encoding=args.encoding,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
