import argparse
import re
from pathlib import Path

import pytest

from submit import ConvertMode, copy_file, copy_directory, parse_dict


class TestSubmit:
    def test_convert_mode(self):
        assert str(ConvertMode.POSITIVE) == "positive"
        assert str(ConvertMode.NEGATIVE) == "negative"
        assert str(ConvertMode.BOTH) == "both"

        assert ConvertMode.get_from_str("positive") == ConvertMode.POSITIVE
        assert ConvertMode.get_from_str("negative") == ConvertMode.NEGATIVE
        assert ConvertMode.get_from_str("both") == ConvertMode.BOTH
        with pytest.raises(argparse.ArgumentTypeError):
            ConvertMode.get_from_str("invalid")

        assert ConvertMode.get_available_values() == [ConvertMode.POSITIVE, ConvertMode.NEGATIVE, ConvertMode.BOTH]

    def test_copy_file(self, source_directory: Path, validate_directory: Path, tmp_path: Path):
        test_adsl = source_directory / "adam" / "adsl.sas"
        validate_adsl = validate_directory / "adam" / "adsl.txt"

        tmp_adsl = tmp_path / "adam" / "adsl.txt"
        copy_file(test_adsl, tmp_adsl)

        with open(tmp_adsl, "r", encoding="utf-8") as f:
            tmp_code = f.read()
        with open(validate_adsl, "r", encoding="utf-8") as f:
            validate_code = f.read()

        assert re.sub(r"\s*", "", tmp_code) == re.sub(r"\s*", "", validate_code)

    def test_copy_directory(self, source_directory: Path, validate_directory: Path, tmp_path: Path):
        copy_directory(
            source_directory, tmp_path, exclude_dirs=["other"], exclude_files=["fcmp.sas"], macro_subs={"id": ""}
        )
        copy_directory(source_directory / "macro", tmp_path / "macro", convert_mode=ConvertMode.NEGATIVE)

        for validate_file in validate_directory.rglob("*.txt"):
            validate_code = validate_file.read_text()
            tmp_code = (tmp_path / validate_file.relative_to(validate_directory)).read_text()

            assert re.sub(r"\s*", "", tmp_code) == re.sub(r"\s*", "", validate_code)

    def test_parse_dict(self):
        assert parse_dict("{a=1}") == {"a": "1"}
        assert parse_dict("{a=1, b=2}") == {"a": "1", "b": "2"}
        with pytest.raises(argparse.ArgumentTypeError):
            parse_dict("{a=1{,} b=2}")
