import json
from pathlib import Path
import pytest
from rst2json import __version__
from rst2json.__main__ import main
from rst2json.core import versioned_meta_strings

DATA_DIR = Path(__file__).with_name("data")

FORMATS = ["html4", "html5", "latex", "xelatex"]


def pytest_generate_tests(metafunc):
    if "fmt" in metafunc.fixturenames:
        argvalues = []
        ids = []
        for fmt in FORMATS:
            for p in (DATA_DIR / fmt).glob("*.rst"):
                input_path = p
                json_path = p.with_suffix(".json")
                conf_path = p.with_suffix(".conf")
                if not conf_path.exists():
                    conf_path = None
                argvalues.append((fmt, input_path, json_path, conf_path))
                ids.append(str(input_path.relative_to(DATA_DIR)))
        metafunc.parametrize(
            "fmt,input_path,json_path,conf_path",
            argvalues,
            ids=ids,
        )


def test_rst2json(capsys, monkeypatch, fmt, input_path, json_path, conf_path):
    with json_path.open() as fp:
        expected = json.load(fp)
    assert "meta" in expected, "'meta' field missing from `expected`"
    assert isinstance(expected["meta"], dict), "'meta' field is not a dict"
    for k, v in versioned_meta_strings.items():
        assert k in expected["meta"], "{k!r} field not in 'meta' dict"
        expected["meta"][k] = v
    args = [
        f"--format={fmt}",
        # --auto-id-prefix needs to be explicitly set because its default value
        # will change in a future version of Docutils
        "--auto-id-prefix=id",
        "--traceback",
    ]
    if conf_path is not None:
        args.append(f"--config={conf_path.relative_to(DATA_DIR)}")
    args.append(str(input_path.relative_to(DATA_DIR)))
    monkeypatch.chdir(DATA_DIR)
    # Override DOCUTILSCONFIG to disable standard/implicit config files
    monkeypatch.setenv("DOCUTILSCONFIG", "")
    main(args)
    stdout, _ = capsys.readouterr()
    output = json.loads(stdout)
    # if output != expected:
    #     with json_path.with_stem(json_path.stem + "_new").open("w") as fp:
    #         json.dump(output, fp)
    assert output == expected


def test_rst2json_usage_error():
    with pytest.raises(SystemExit) as excinfo:
        main(["--format"])
    assert "--format option missing required argument" in str(excinfo.value)


def test_rst2json_version(capsys):
    main(["--version"])
    stdout, _ = capsys.readouterr()
    assert stdout == f"rst2json {__version__}\n"


def test_rst2json_config_via_options(capsys, monkeypatch):
    FORMAT = "html4"
    INPUT = DATA_DIR / FORMAT / "configged.rst"
    with INPUT.with_suffix(".json").open() as fp:
        expected = json.load(fp)
    assert "meta" in expected, "'meta' field missing from `expected`"
    assert isinstance(expected["meta"], dict), "'meta' field is not a dict"
    for k, v in versioned_meta_strings.items():
        assert k in expected["meta"], "{k!r} field not in 'meta' dict"
        expected["meta"][k] = v
    args = [
        f"--format={FORMAT}",
        # --auto-id-prefix needs to be explicitly set because its default value
        # will change in a future version of Docutils
        "--auto-id-prefix=id",
        "--traceback",
        "--smart-quotes=yes",
        "--no-doc-title",
        "--section-subtitles",
        str(INPUT.relative_to(DATA_DIR)),
    ]
    monkeypatch.chdir(DATA_DIR)
    # Override DOCUTILSCONFIG to disable standard/implicit config files
    monkeypatch.setenv("DOCUTILSCONFIG", "")
    main(args)
    stdout, _ = capsys.readouterr()
    output = json.loads(stdout)
    assert output == expected
