from pathlib import Path

from click.testing import CliRunner

from submit.submit import cli


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


def test_copydir_with_merge(tmp_path: Path, dummy_sas_dir: Path) -> None:
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
