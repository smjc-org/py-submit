import re
from pathlib import Path

from submit import ConvertMode, copy_file, copy_directory


class TestSubmit:
    def test_copy_file(self, shared_test_directory: Path, shared_validate_directory: Path, tmp_path: Path):
        test_adsl = shared_test_directory / "adam" / "adsl.sas"
        validate_adsl = shared_validate_directory / "adam" / "adsl.txt"

        tmp_adsl = tmp_path / "adam" / "adsl.txt"
        copy_file(test_adsl, tmp_adsl)

        with open(tmp_adsl, "r", encoding="utf-8") as f:
            tmp_code = f.read()
        with open(validate_adsl, "r", encoding="utf-8") as f:
            validate_code = f.read()

        assert re.sub(r"\s*", "", tmp_code) == re.sub(r"\s*", "", validate_code)

    def test_copy_directory(self, shared_test_directory: Path, shared_validate_directory: Path, tmp_path: Path):
        copy_directory(
            shared_test_directory, tmp_path, exclude_dirs=["other"], exclude_files=["fcmp.sas"], macro_subs={"id": ""}
        )
        copy_directory(shared_test_directory / "macro", tmp_path / "macro", convert_mode=ConvertMode.NEGATIVE)

        for validate_file in shared_validate_directory.rglob("*.txt"):
            validate_code = validate_file.read_text()
            tmp_code = (tmp_path / validate_file.relative_to(shared_validate_directory)).read_text()

            assert re.sub(r"\s*", "", tmp_code) == re.sub(r"\s*", "", validate_code)


def main():
    test_list = [func for name, func in globals().items() if callable(func) and name.startswith("test_")]
    try:
        for test in test_list:
            test()
    except AssertionError:
        print("Test failed.")
    else:
        print("All tests passed.")


if __name__ == "__main__":
    main()
