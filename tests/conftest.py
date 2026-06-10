from pathlib import Path

import pytest


@pytest.fixture
def dummy_sas_dir(tmp_path: Path) -> Path:
    """动态创建一个包含 sas 文件的目录。"""

    src_dir = tmp_path / "sas_src"
    src_dir.mkdir()

    # 包含 POSITIVE 标记的文件
    file = src_dir / "t_6_1.sas"
    file.write_text("data _null_;\n/*SUBMIT BEGIN*/\nproc print data=sashelp.class;\nrun;\n/*SUBMIT END*/\nrun;", encoding="gbk")

    # 包含 NEGATIVE 标记的文件
    file = src_dir / "t_6_2.sas"
    file.write_text("/*NOT SUBMIT BEGIN*/\noptions nodate;\n/*NOT SUBMIT END*/\nproc means data=test; run;", encoding="gbk")

    # 包含不完整 POSITIVE 标记的文件
    file = src_dir / "t_6_3.sas"
    file.write_text("/*SUBMIT BEGIN*/\nproc print data=sashelp.class;\nrun;", encoding="gbk")

    file = src_dir / "t_6_4.sas"
    file.write_text("proc print data=sashelp.class;\nrun;\n/*SUBMIT END*/", encoding="gbk")

    # 包含不完整 NEGATIVE 标记的文件
    file = src_dir / "t_6_5.sas"
    file.write_text("/*NOT SUBMIT BEGIN*/\noptions nodate;\nproc means data=test; run;", encoding="gbk")

    file = src_dir / "t_6_6.sas"
    file.write_text("proc means; run;\n/*NOT SUBMIT END*/", encoding="gbk")

    # 不包含任何标记的文件
    file = src_dir / "t_6_7.sas"
    file.write_text("proc means; run;", encoding="gbk")

    # 包含宏变量的文件
    file = src_dir / "t_6_7.sas"
    file.write_text("data _null_;\n/*SUBMIT BEGIN*/\nproc print data=&indata;\nrun;&&indata;&indatabase;\n/*SUBMIT END*/\nrun;")

    # 在子目录里的文件（用于测试 --exclude-dir 参数）
    sub_dir = src_dir / "sponser_only"
    sub_dir.mkdir()
    file = sub_dir / "t_7_1.sas"
    file.write_text("proc gplot; run;", encoding="gbk")

    # 不需要转换的文件（用于测试 --exclude-file 参数）
    file = src_dir / "deprecated_t_8_1.sas"
    file.write_text("proc means; run;", encoding="gbk")

    return src_dir
