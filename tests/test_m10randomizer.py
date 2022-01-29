import pytest
from commands import m10randomizer


def test_exec():
    # 雑に100回回しても例外が出ない
    for _ in range(100):
        assert len(m10randomizer.exec()) > 0


@pytest.mark.parametrize(
    ("candidate", "hp", "atk", "dfs", "agi", "swords", "expected"),
    [
        ("A", 0, 0, 0, 0, "", "斬"),  # 攻撃があるなら直接攻撃
        ("熱", 0, 0, 0, 0, "魔", "斬"),  # 攻撃があるなら直接攻撃
        ("A", 0, 0, 0, 0, "斬", ""),  # 攻撃があるなら直接攻撃
        ("熱", 0, 0, 0, 0, "魔斬", ""),  # 攻撃があるなら直接攻撃
        ("S", 0, 0, 0, 0, "", "斬"),  # 素早さがあるなら剣
        ("S", 0, 0, 0, 0, "斬", ""),  # 素早さがあるなら剣
        ("sword", 0, 0, 0, 0, "", "S"),  # 剣があるなら素早さが必要
    ],
)
def test_verify_useless(candidate: str, hp, atk, dfs, agi, swords, expected, mocker):
    receive = mocker.patch("random.choice", return_value="斬")
    assert (
        m10randomizer.verify_useless(candidate, hp, atk, dfs, agi, swords) == expected
    )


@pytest.mark.parametrize(
    ("agi", "swords", "expected"),
    [
        (0, "", True),
        (0, "速", False),
        (1, "", True),
        (1, "斬", True),
        (1, "斬斬", False),
        (2, "斬速斬斬斬", True),
        (2, "斬斬速斬斬", False),
    ],
)
def test_verify_aizawa(agi, swords, expected):
    assert m10randomizer.verify_aizawa(agi, swords) == expected


@pytest.mark.parametrize(
    ("agi", "swords", "expected"),
    [
        (0, "", ""),
        (1, "", ""),
        (1, "斬死", "斬死"),
        (1, "死死死斬", "斬"),
        (2, "斬死死死斬", "斬斬"),
        (2, "死", ""),
    ],
)
def test_remove_limited(agi, swords, expected):
    assert m10randomizer.remove_limited(agi, swords) == expected
