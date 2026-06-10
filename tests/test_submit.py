from pathlib import Path

from click.testing import CliRunner

from submit.submit import cli


def test_cutcode_incomplete_comment(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 cutcode 对不完整标记的识别"""

    runner = CliRunner()

    txt_dir = tmp_path / "txt_out"

    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(dummy_sas_dir),
            "-t",
            str(txt_dir),
        ],
    )

    assert result.exit_code == 0

    assert "存在 POSITIVE 模式的起始注释，但未找到对应的终止注释" in result.stderr
    assert "存在 POSITIVE 模式的终止注释，但未找到对应的起始注释" in result.stderr
    assert "存在 NEGATIVE 模式的起始注释，但未找到对应的终止注释" in result.stderr
    assert "存在 NEGATIVE 模式的终止注释，但未找到对应的起始注释" in result.stderr
    assert "未找到预期的 POSITIVE 模式的注释" in result.stderr


def test_cutcode_missing_positive_comment_with_allow_missing_positive(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 cutcode 对缺少 POSITIVE 模式的注释 + --allow-missing-positive 参数的处理"""

    runner = CliRunner()

    txt_dir = tmp_path / "txt_out"

    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(dummy_sas_dir),
            "-t",
            str(txt_dir),
            "--allow-missing-positive",
        ],
    )

    assert result.exit_code == 0

    assert "未找到预期的 POSITIVE 模式的注释" not in result.stderr
    assert "存在 POSITIVE 模式的起始注释，但未找到对应的终止注释" not in result.stderr
    assert "存在 POSITIVE 模式的终止注释，但未找到对应的起始注释" not in result.stderr
    assert "存在 NEGATIVE 模式的起始注释，但未找到对应的终止注释" in result.stderr
    assert "存在 NEGATIVE 模式的终止注释，但未找到对应的起始注释" in result.stderr


def test_copyfile(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copyfile 命令"""

    runner = CliRunner()

    sas_file = dummy_sas_dir / "t_6_1.sas"
    txt_file = tmp_path / "t_6_1.txt"

    # 使用 runner.invoke 触发命令
    result = runner.invoke(
        cli,
        [
            "copyfile",
            "-s",
            str(sas_file),
            "-t",
            str(txt_file),
        ],
    )

    assert result.exit_code == 0

    assert txt_file.exists()
    content = txt_file.read_text(encoding="gbk")
    assert "proc print data=sashelp.class;" in content
    assert "data _null_;" not in content


def test_copyfile_with_substitute(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copyfile 命令，带上 --substitute 参数"""

    runner = CliRunner()

    sas_file = dummy_sas_dir / "t_6_7.sas"
    txt_file = tmp_path / "t_6_7.txt"

    result = runner.invoke(
        cli,
        [
            "copyfile",
            "-s",
            str(sas_file),
            "-t",
            str(txt_file),
            "-sub",
            "indata",
            "adsl",
        ],
    )

    assert result.exit_code == 0

    assert txt_file.exists()

    content = txt_file.read_text(encoding="gbk")

    # &indata 被替换成 adsl
    assert "proc print data=adsl;" in content

    # &&indata 没有被替换
    assert "&&indata" in content

    # &indatabase 没有被替换
    assert "&indatabase" in content


def test_copydir_with_exclude_file(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copydir 命令，带上 --exclude-file 参数"""

    runner = CliRunner()

    txt_dir = tmp_path / "txt_out"

    # 运行 copydir 命令，排除以 deprecated 开头的文件
    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(dummy_sas_dir),
            "-t",
            str(txt_dir),
            "--exclude-file",
            "deprecated*.sas",
        ],
    )

    assert result.exit_code == 0

    # t_6_1.sas 没有被排除 -> 应该生成对应的 txt
    assert (txt_dir / "t_6_1.txt").exists()

    # deprecated_t_8_1.sas 被排除了 -> 不应该生成对应的 txt
    assert not (txt_dir / "deprecated_t_8_1.txt").exists()


def test_copydir_with_exclude_dirs(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copydir 命令，带上 --exclude-dir 参数"""

    runner = CliRunner()

    txt_dir = tmp_path / "txt_out"

    # 运行 copydir 命令，排除以 deprecated 开头的文件
    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(dummy_sas_dir),
            "-t",
            str(txt_dir),
            "--exclude-dir",
            "sponser_only",
        ],
    )

    assert result.exit_code == 0

    # t_7_1.sas 被排除了 -> 不应该生成对应的 txt
    assert not (txt_dir / "t_7_1.txt").exists()


def test_copydir_with_substitute(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copydir 命令，带上 --substitute 参数"""

    runner = CliRunner()

    txt_dir = tmp_path / "txt_out"

    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(dummy_sas_dir),
            "-t",
            str(txt_dir),
            "-sub",
            "indata",
            "adsl",
        ],
    )

    assert result.exit_code == 0

    txt_file = txt_dir / "t_6_7.txt"

    assert txt_file.exists()

    content = txt_file.read_text(encoding="gbk")

    # &indata 被替换成 adsl
    assert "proc print data=adsl;" in content

    # &&indata 没有被替换
    assert "&&indata" in content

    # &indatabase 没有被替换
    assert "&indatabase" in content


def test_copydir_with_merge(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copydir 命令，带上 --merge 参数"""

    runner = CliRunner()

    txt_dir = tmp_path / "txt_out"

    # 运行 copydir 命令，排除以 deprecated 开头的文件
    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(dummy_sas_dir),
            "-t",
            str(txt_dir),
            "--exclude-dir",
            "sponser_only",
            "--exclude-file",
            "deprecated*.sas",
            "--merge",
            "--merge-name",
            "合并代码.txt",
        ],
    )

    assert result.exit_code == 0

    merge_file = txt_dir / "合并代码.txt"
    assert merge_file.exists()

    # 验证合并代码中的内容是否包含特定字符串
    merge_content = merge_file.read_text(encoding="gbk")
    assert "/*====================t_6_1.sas====================*/" in merge_content


def test_copydir_no_files_need_process(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copydir 命令，没有需要处理的文件时"""

    runner = CliRunner()

    txt_dir = tmp_path / "txt_out"

    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(dummy_sas_dir),
            "-t",
            str(txt_dir),
            "--exclude-file",
            "**/*.sas",
        ],
    )

    assert result.exit_code == 0

    assert "未找到需要处理的 .sas 文件" in result.stdout


def test_copydir_output_dir_equal_input_dir(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copydir 命令，输出目录与输入目录是同一目录"""

    runner = CliRunner()

    txt_dir = dummy_sas_dir / "sponser_only"

    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(dummy_sas_dir),
            "-t",
            str(txt_dir),
        ],
    )

    assert result.exit_code == 0

    assert "当前目录与指定输出 TXT 的目录是同一目录" in result.stdout


def test_copydir_output_dir_inside_input_dir(dummy_sas_dir: Path, tmp_path: Path) -> None:
    """测试 copydir 命令，输出目录在输入目录内"""

    runner = CliRunner()

    sas_dir = dummy_sas_dir / "sponser_only"
    txt_dir = dummy_sas_dir

    result = runner.invoke(
        cli,
        [
            "copydir",
            "-s",
            str(sas_dir),
            "-t",
            str(txt_dir),
        ],
    )

    assert result.exit_code == 0

    assert "当前目录在指定输出 TXT 的目录内" in result.stdout
