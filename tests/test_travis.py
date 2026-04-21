from __future__ import annotations

import difflib
import sys
import sysconfig

from pathlib import Path
import shutil

import pytest

from numjuggler.main import main

HERE = Path(__file__).parent.absolute()
data = HERE / "data/travis_tests"
assert data.exists(), "Cannot access test data 'travis' files"


@pytest.mark.parametrize(
    "mode,options,inp",
    [
        (
            "renum",
            "-c 10 -s 5 -m 100",
            "i1",
        ),
        (
            "renum",
            "-c i -s i -m i",
            "i2",
        ),
        (
            "renum",
            "-u -5942",
            "i3",
        ),
        (
            "remh",
            "",
            "nested_complement",
        ),
    ],
)
def test_travis(cd_tmpdir, capsys, mode, options, inp):
    subdir = data / mode
    source = subdir / (inp + ".i")
    wrk_file = shutil.copy(source, cd_tmpdir)
    ref_path = subdir / (inp + ".ref")
    command = ["--mode", mode, *options.split(), wrk_file]
    main(command)
    out, _ = capsys.readouterr()
    _assert_equal(out, ref_path)


cdense_data = Path(data / "cdens")


@pytest.mark.parametrize("inp", ["inp"])
@pytest.mark.parametrize("map_", [f"map{x}" for x in range(1, 7)])
def test_cdens(cd_tmpdir, capsys, inp, map_):
    source = cdense_data / (inp + ".i")
    wrk_file = shutil.copy(source, cd_tmpdir)
    wrk_map = shutil.copy(cdense_data / map_, cd_tmpdir)
    ref_path = cdense_data / f"{inp}.{map_}.ref"
    command = ["--mode", "cdens", "--map", wrk_map, wrk_file]
    main(command)
    out, _ = capsys.readouterr()
    _assert_equal(out, ref_path)


merge_data = Path(data / "merge")


@pytest.mark.parametrize("inp,merged", [("inp", "merged")])
def test_merge(cd_tmpdir, capsys, inp, merged):
    inp2_path = merge_data / (inp + "2.inp")
    inp1_path = merge_data / (inp + "1.inp")
    wrk_inp2 = shutil.copy(inp2_path, cd_tmpdir)
    wrk_inp1 = shutil.copy(inp1_path, cd_tmpdir)
    ref_path = merge_data / f"{merged}.{inp}.ref"
    command = ["--mode", "merge", "-m", wrk_inp2, wrk_inp1]
    main(command)
    out, _ = capsys.readouterr()
    _assert_equal(out, ref_path)


def _assert_equal(out: str, ref_path: Path) -> None:
    name = ref_path.name
    with ref_path.open(encoding="utf8") as f:
        for i, (o, r) in enumerate(zip(out.split("\n"), f.readlines())):
            assert o.strip() == r.strip(), (
                f"{name}:{i + 1} {'\n'.join(difflib.Differ().compare([o], [r]))}"
            )
