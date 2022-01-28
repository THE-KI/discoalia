import random

CANDIDATES = ['hp','atk','dfs','agi','sword']
M10_SWORDS = ['斬','衝','絶','魔','死','熱','護','速','鏡','命',]

def exec():
    heart = 10 # 途心
    hp = 0
    atk = 0
    dfs = 0
    agi = 0
    swords = ''

    for i in range(heart):
        candidate = random.choice(CANDIDATES)
        if candidate == 'hp':
            hp += 5
        elif candidate == 'atk':
            atk += 1
        elif candidate == 'dfs':
            dfs += 1
        elif candidate == 'agi':
            agi += 1
        elif candidate == 'sword':
            swords += random.choice(M10_SWORDS)

    return f"{hp}/{atk}/{dfs}/{agi}/{swords}"

if __name__ == '__main__':
    print(exec())