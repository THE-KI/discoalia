import random
import re
import requests
from bs4 import BeautifulSoup

room_name = ""
room_heart = 10
room_inscription_lower = 0
room_inscription_upper = 0
room_swords = []
room_swords_min_inscription = 0  # その部屋で最小の銘コスト
hp_upper = None
atk_upper = None
dfs_upper = None
agi_upper = None
required = None

# 1 [！]: 【必須】戦闘準備(0)<銘1>
sword_reg = r"[0-9]+ \[(.+)\]: (.+)\(([0-9]+)\)(?:<銘([0-9]+)>)?"
sword_pat = re.compile(sword_reg)
# 【必須】戦闘準備(0)
require_reg = r"(.+)\([0-9]+\)"
require_pat = re.compile(require_reg)
# 銘の範囲[ 1 ～ 1 ]
inscription_reg = r"銘の範囲\[ ([0-9]+) 〜 ([0-9]+) \]"
inscription_pat = re.compile(inscription_reg)
# ＨＰ0 　 攻撃力0 　 防御力0 　 素早さ0
status_reg = r"ＨＰ([0-9]+)\s+攻撃力([0-9]+)\s+防御力([0-9]+)\s+素早さ([0-9]+)"
status_pat = re.compile(status_reg)


class RoomSword:
    def __init__(self, sword_str: str):
        matchObj = sword_pat.search(sword_str)
        self.c = matchObj.group(1)
        self.name = matchObj.group(2)
        self.heart = int(matchObj.group(3))
        self.inscription = int(matchObj.group(4)) if matchObj.group(4) else None


def exec(room_id: int, user_name: str):
    get_room_info(room_id)
    return get_expression(user_name)


def get_room_info(room_id: int):
    global required
    global room_name
    global room_heart
    global room_inscription_lower
    global room_inscription_upper
    global hp_upper
    global atk_upper
    global dfs_upper
    global agi_upper

    print("start read http://stara.mydns.jp/draw_roomrule.php?id=" + str(room_id))
    html_source = requests.get(
        "http://stara.mydns.jp/draw_roomrule.php?id=" + str(room_id)
    )
    html_source.encoding = html_source.apparent_encoding
    soup = BeautifulSoup(html_source.text, "html.parser")
    print("end read php")

    room_name = soup.find("td", text="部屋名").find_next_sibling("td").text

    get_room_swords(
        soup.find("td", text="使用できる剣").find_next_sibling("td").find_all("tr")
    )
    if len(room_swords) == 0:
        return "剣情報が取得できませんでした。そんな部屋番号あります？"

    preview_required = soup.find("td", text="使用必須の剣")
    if preview_required:
        matchObj = require_pat.search(preview_required.find_next_sibling("td").text)
        if matchObj:
            for sword in room_swords:
                if sword.name == matchObj.group(1):
                    required = sword
                    break

    room_heart = int(soup.find("td", text="途心設定").find_next_sibling("td").text)

    preview_inscription = soup.find("td", text="銘設定")
    if preview_inscription:
        matchObj = inscription_pat.search(
            preview_inscription.find_next_sibling("td").text
        )
        if matchObj:
            room_inscription_lower = int(matchObj.group(1))
            room_inscription_upper = int(matchObj.group(2))

    preview_status = soup.find("td", text="ステータス上限")
    if preview_status:
        matchObj = status_pat.search(preview_status.find_next_sibling("td").text)
        if matchObj:
            hp_upper = int(matchObj.group(1))
            atk_upper = int(matchObj.group(2))
            dfs_upper = int(matchObj.group(3))
            agi_upper = int(matchObj.group(4))


def get_room_swords(trs):
    global room_swords
    global room_swords_min_inscription
    for tr in trs:
        if tr.td:
            sword = RoomSword(tr.td.text)
            room_swords.append(sword)
            if sword.inscription and (
                room_swords_min_inscription is None
                or room_swords_min_inscription > sword.inscription
            ):
                room_swords_min_inscription = sword.inscription


def get_expression(user_name: str):

    hp = atk = dfs = agi = 0
    heart = 0
    swords = ""
    unit_name = user_name.replace("/", "／")

    # まずは必須剣。
    if required:
        swords += required.c
        heart += required.heart

    total_inscription = 0
    while total_inscription < room_inscription_lower:
        rest_inscription_upper = room_inscription_upper - total_inscription
        rest_inscription_lower = room_inscription_lower - total_inscription
        # 銘コスト条件をまだ満たさないなら、他の銘剣を入れる余地を残す必要がある
        # 銘コスト5～5の部屋の最小銘剣が銘2、そしてすでに銘2が入っている時、更に銘2を入れてしまうと銘4になり条件達成が不可になる
        candidates = list(
            filter(
                lambda s: s.inscription
                and (
                    rest_inscription_upper >= s.inscription >= rest_inscription_lower
                    or rest_inscription_upper - room_swords_min_inscription
                    >= s.inscription
                ),
                room_swords,
            )
        )
        if len(candidates) == 0:
            return f"銘コストの計算が難しかったです。f{swords}"
        s = random.choice(candidates)
        swords += s.c
        heart += s.heart
        total_inscription += s.inscription
        if total_inscription > room_inscription_upper:
            return f"銘コストの計算が難しかったです。f{swords}"
    rest_inscription = room_inscription_upper - total_inscription

    if heart > room_heart:
        return f"必須剣と銘剣入れるだけで途心オーバーしちゃった。f{swords}"

    while heart < room_heart:
        candidates = []
        if hp_upper is None or hp < hp_upper:
            candidates.append("H")
        if atk_upper is None or atk < atk_upper:
            candidates.append("A")
        if dfs_upper is None or dfs < dfs_upper:
            candidates.append("D")
        if agi_upper is None or agi < agi_upper:
            candidates.append("S")

        # 銘および途心が十分な剣を選択
        sword_candidates = list(
            filter(
                lambda s: (
                    s.inscription is None
                    or (room_inscription_upper - total_inscription) >= s.inscription
                )
                and (room_heart - heart >= s.heart),
                room_swords,
            )
        )
        if len(sword_candidates) > 0:
            candidates.append("sword")

        if len(candidates) == 0:
            return f"作成に失敗しました。途中経過: {hp}/{atk}/{dfs}/{agi}/{swords}"

        choice = random.choice(candidates)
        if "H" in choice:
            hp += 5
            heart += 1
        elif "A" in choice:
            atk += 1
            heart += 1
        elif "D" in choice:
            dfs += 1
            heart += 1
        elif "S" in choice:
            agi += 1
            heart += 1
        else:
            choice_sword = random.choice(sword_candidates)
            swords += choice_sword.c
            heart += choice_sword.heart
            total_inscription += (
                choice_sword.inscription if choice_sword.inscription else 0
            )

    # ここで剣をランダムソート。銘とか必須剣が前に固まるので。
    swords = "".join(random.sample(swords, len(swords)))

    expression = f"{hp}/{atk}/{dfs}/{agi}/{swords}/{unit_name}（{room_name}）"

    return expression


if __name__ == "__main__":
    print(exec(796, "name"))
