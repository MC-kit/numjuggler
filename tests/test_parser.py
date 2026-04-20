from io import StringIO

import pytest

from numjuggler.parser import Card, index_


class TestCardParser:
    def test_vol_param(self):
        definition = [
            "600177 400 -1.00000e+00 $ WATER_LEFT\n",
            "          600003 -600421 601230 -600013 600011\n",
            "           Vol=1.335972e+01\n",
            "           imp:n=1.0   imp:p=1.0   U=5972  \n",
        ]

        cell2 = Card(definition, ctype=3, pos=1)
        cell2.get_values()

        cell2._set_value_by_type("u", 30)
        assert "U=30" in cell2.card()
        assert "Vol=1.335972e+01" in cell2.card()


@pytest.mark.parametrize("text, expected", [
    ("*tr14", "*tr14"),
    ("90.0", "90.0"),
    ("*tr14  $", "*tr14  "),
])
def test_index_(text, expected):
    i = index_(text)
    actual = text[:i]
    assert actual == expected

def test_separate_label_spec():
    spec = [
        "*tr14",
        "       0   0    0"
        "      11.25 78.75 90.0",
        "     101.25 11.25 90.0",
        "      90.0  90.0   0.0",
    ]
    out = StringIO()
    transformation = Card(spec, ctype=5, pos=1, debug=out)
    value = transformation.input[0]
    assert value == "*tr14"
    assert "Line" in out.getvalue()
