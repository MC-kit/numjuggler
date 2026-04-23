from io import StringIO

import pytest

from numjuggler.parser import Card, CID


@pytest.fixture
def card_600177() -> Card:
    definition = [
        "600177 400 -1.00000e+00 $ WATER_LEFT\n",
        "          600003 -600421 601230 -600013 600011\n",
        "           Vol=1.335972e+01\n",
        "           imp:n=1.0   imp:p=1.0   U=5972  \n",
    ]
    card = Card(definition, ctype=3, pos=1, debug=StringIO())
    card.get_values()  # dvp: as in the old test, why not in constructor?
    return card


def test_vol_param(card_600177: Card):
    assert "Vol=1.335972e+01" in card_600177.card()


def test_get_set_value(card_600177: Card):
    assert card_600177._get_value_by_type("u") == 5972
    assert card_600177._get_value_by_type("_not_existing") is None
    card_600177._set_value_by_type("u", 30)
    assert "U=30" in card_600177.card()
    assert card_600177._get_value_by_type("u") == 30


def test_print_debug(card_600177: Card):
    debug_text = card_600177.debug.getvalue()
    assert "Line" in debug_text


def test_card_get_inpt_with_bad_character():
    log = StringIO()
    card = Card(["1\t0 1"], ctype=3, pos=1, debug=log)
    card.get_input(check_bad_chars=True)
    assert "get_input: bad char" in log.getvalue()
    card = Card(["1\t0 1"], ctype=3, pos=1, debug=None)
    with pytest.raises(ValueError, match="Bad character"):
        card.get_input(check_bad_chars=True)


def test_suffix_and_prefix_properties():
    card = Card(["1 0 1\n"], ctype=3, pos=1)
    card.get_values()
    assert card.geom_prefix == ""
    assert card.geom_suffix == ""
    card.geom_prefix = "pfx"
    card.geom_suffix = "sfx"
    assert card.geom_prefix == "pfx"
    assert card.geom_suffix == "sfx"


def test_fc_card():
    log = StringIO()
    card = Card(["fc4 xxx\n"], ctype=5, pos=1, debug=log)
    card.get_values()
    card.get_input()
    log_result = log.getvalue()
    assert "xxx" in log_result


def test_card_get_refcells():
    card = Card(["1 0 1\n"], ctype=3, pos=1)
    card.get_values()
    # card.get_input()
    actual = card.get_refcells()
    assert actual == {1}
    card = Card(["1 0 1 #2\n"], ctype=3, pos=1)
    card.get_values()
    # card.get_input()
    actual = card.get_refcells()
    assert actual == {1, 2}


def test_card_get_geom():
    card = Card(["1 0 1\n"], ctype=3, pos=1)
    card.get_values()
    geom = card.get_geom()
    assert geom.strip() == "1"


def test_card_get_u():
    card = Card(["1 0 1\n"], ctype=3, pos=1)
    card.get_values()
    universe = card.get_u()
    assert universe is None
    card = Card(
        [
            "1 0 1\n",
            "        u=200\n",
        ],
        ctype=3,
        pos=1,
    )
    card.get_values()
    universe = card.get_u()
    assert universe == 200


def test_card_get_f():
    card = Card(["1 0 1\n"], ctype=3, pos=1)
    card.get_values()
    assert card.get_f() is None
    card = Card(
        [
            "1 0 1\n",
            "        fill=200\n",
        ],
        ctype=3,
        pos=1,
    )
    card.get_values()
    assert card.get_f() == 200
    assert card.get_f(300) == 300
    assert card.get_f() == 300
    assert card._get_value_by_type("fill") == 300


@pytest.mark.parametrize(
    "value, expected_name",
    [
        (-1, "comment"),
        (-2, "blankline"),
        (1, "message"),
        (2, "title"),
        (3, "cell"),
        (4, "surface"),
        (5, "data"),
    ],
)
def test_cid(value, expected_name):
    assert CID.get_name(value) == expected_name


def test_cid_bad_path():
    with pytest.raises(ValueError, match="No CID names with value 100"):
        CID.get_name(100)
