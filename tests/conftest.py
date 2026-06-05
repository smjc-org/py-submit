from pathlib import Path

import pytest


@pytest.fixture
def dummy_sas_dir(tmp_path: Path) -> Path:
    """动态创建一个包含 sas 文件的目录。"""

    src_dir = tmp_path / "sas_src"
    src_dir.mkdir()

    # 1. 创建一个包含 POSITIVE 标记的文件
    file_1 = src_dir / "t_6_1.sas"
    file_1.write_text("data _null_;\n/*SUBMIT BEGIN*/\nproc print data=sashelp.class;\nrun;\n/*SUBMIT END*/\nrun;", encoding="gbk")

    # 2. 创建一个包含 NEGATIVE 标记的文件
    file2 = src_dir / "t_6_2.sas"
    file2.write_text("/*NOT SUBMIT BEGIN*/\noptions nodate;\n/*NOT SUBMIT END*/\nproc means data=test; run;", encoding="gbk")

    # 3. 创建一个在子目录里的文件（用于测试 --exclude-dir 参数）
    sub_dir = src_dir / "sponser_only"
    sub_dir.mkdir()
    file3 = sub_dir / "t_7_1.sas"
    file3.write_text("proc gplot; run;", encoding="gbk")

    # 4. 创建一个不需要转换的文件（用于测试 --exclude-file 参数）
    file3 = src_dir / "deprecated_t_8_1.sas"
    file3.write_text("proc means; run;", encoding="gbk")

    return src_dir
