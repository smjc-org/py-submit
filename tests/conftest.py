from pathlib import Path

import pytest

from tests.contents_source import (
    content_source_adsl,
    content_source_addv,
    content_source_t1,
    content_source_t2,
    content_source_t3,
    content_source_macro1,
    content_source_macro2,
    content_source_q1,
    content_source_q2,
    content_source_fcmp,
    content_source_other,
)

from tests.contents_validate import (
    content_validate_adsl,
    content_validate_addv,
    content_validate_t1,
    content_validate_t2,
    content_validate_t3,
    content_validate_macro1,
    content_validate_macro2,
)


@pytest.fixture(scope="session")
def shared_source_directory(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp("code")
    dir_adam = dir / "adam"
    dir_tfl = dir / "tfl"
    dir_macro = dir / "macro"
    dir_other = dir / "other"

    # adam sas files
    dir_adam.mkdir()
    (dir_adam / "adsl.sas").write_text(content_source_adsl)
    (dir_adam / "adae.sas").write_text(content_source_addv)

    # tfl sas files
    dir_tfl.mkdir()
    (dir_tfl / "t1.sas").write_text(content_source_t1)
    (dir_tfl / "t2.sas").write_text(content_source_t2)
    (dir_tfl / "t3.sas").write_text(content_source_t3)

    # macro sas files
    dir_macro.mkdir()
    (dir_macro / "macro1.sas").write_text(content_source_macro1)
    (dir_macro / "macro2.sas").write_text(content_source_macro2)

    # other directories which supposed to be excluded
    dir_other.mkdir()
    (dir_other / "q1.sas").write_text(content_source_q1)
    (dir_other / "q2.sas").write_text(content_source_q2)

    # other sas files which supposed to be excluded
    (dir / "fcmp.sas").write_text(content_source_fcmp)

    # other files whose suffix is not sas
    (dir / "other.txt").write_text(content_source_other)
    return dir


@pytest.fixture(scope="session")
def shared_validate_directory(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp("validate")
    dir_adam = dir / "adam"
    dir_tfl = dir / "tfl"
    dir_macro = dir / "macro"

    # adam txt files
    dir_adam.mkdir()
    (dir_adam / "adsl.txt").write_text(content_validate_adsl)
    (dir_adam / "adae.txt").write_text(content_validate_addv)

    # tfl txt files
    dir_tfl.mkdir()
    (dir_tfl / "t1.txt").write_text(content_validate_t1)
    (dir_tfl / "t2.txt").write_text(content_validate_t2)
    (dir_tfl / "t3.txt").write_text(content_validate_t3)

    # macro txt files
    dir_macro.mkdir()
    (dir_macro / "macro1.txt").write_text(content_validate_macro1)
    (dir_macro / "macro2.txt").write_text(content_validate_macro2)
    return dir
