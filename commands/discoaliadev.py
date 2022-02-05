import random
import re

"""
今のコマンドに影響を与えず開発するためのデバッグコマンド。
git管理するとこれの差分出るのすごい恥ずかしいね。pushはするけど今後addしないと思う
"""

CANDIDATES = ["H", "A", "D", "S", "sword"]
M10_SWORDS = [
    "斬",
    "衝",
    "絶",
    "魔",
    "死",
    "熱",
    "護",
    "速",
    "鏡",
    "命",
]
DIRECT_ATTACK_SWORDS = [
    "斬",
    "衝",
    "絶",
]

MAX_HEART = 10


def exec(user_name: str):
    atk = dfs = agi = 0
    hp = 5
    heart = 1
    swords = ""
    unit_name = user_name.replace("/", "／")

    while heart < MAX_HEART:
        choice = random.choice(CANDIDATES)
        if choice == "sword":
            choice = random.choice(M10_SWORDS)

        # print(f"{hp}/{atk}/{dfs}/{agi}/{swords}...{heart}")
        choice += verify_useless(choice, hp, atk, dfs, agi, swords)
        heart += len(choice)

        # 補正をかけて途心オーバーしたらリセット
        if heart > MAX_HEART:
            atk = dfs = agi = 0
            hp = 5
            heart = 1
            swords = ""
            continue

        if "H" in choice:
            hp += 5
            choice = choice.replace("H", "")
        if "A" in choice:
            atk += 1
            choice = choice.replace("A", "")
        if "D" in choice:
            dfs += 1
            choice = choice.replace("D", "")
        if "S" in choice:
            agi += 1
            choice = choice.replace("S", "")
        if len(choice) != 0:
            swords += choice

    expression = f"{hp}/{atk}/{dfs}/{agi}/{swords}/{unit_name}"

    if not verify_aizawa(agi, swords):
        # print("detected aizawa. " + expression)
        expression = exec()

    return expression


def verify_useless(candidate: str, hp, atk, dfs, agi, swords):
    """無駄要素がないかをチェック。あればステータスに補正をかけて、増えた分の途心を返す"""
    if (
        candidate in ["A", "熱"]
        and re.search(r"[" + ("".join(DIRECT_ATTACK_SWORDS)) + "]", swords) == None
    ):
        # 攻撃力があるなら直接攻撃剣が必要
        return random.choice(DIRECT_ATTACK_SWORDS)
    elif candidate == "S" and len(swords) == 0:
        # 素早さがあるなら剣が必要
        return random.choice(M10_SWORDS)
    elif candidate == "sword":
        # 剣があるなら素早さが必要
        ret_value = ""
        if agi == 0:
            return "S"
    return ""


def verify_aizawa(agi: int, swords):
    """あいざわチェック。Trueなら非あいざわ"""
    removed_swords = remove_limited(agi, swords)
    if "速" in removed_swords[:agi]:
        return True
    if len(removed_swords) <= agi:
        return True
    return False


def remove_limited(agi: int, swords):
    """agiの範囲で使用可能なリミテッド剣を削除し、残った剣の配列を返す"""
    LIMITEDS = [
        "魔",
        "死",
        "鏡",
        "命",
    ]

    for i in range(min(agi, len(swords))):
        if swords[i] in LIMITEDS:
            swords = swords[:i] + swords[i + 1 :]
            return remove_limited(agi, swords)
    return swords


if __name__ == "__main__":
    print(exec("あああ/いいい/ううう"))
