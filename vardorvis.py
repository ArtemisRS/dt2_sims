# Written by GfHaver

import math
import random
import statistics

class Player:
    def __init__(self, slash_atk, slash_def, str_bonus, is_fang = True, recoil=False, justiciar = False, bf = False):
        self.slash_atk = slash_atk
        self.slash_def = slash_def
        self.max_hp = 99
        self.current_hp = 99
        self.str_bonus = str_bonus
        self.is_fang = is_fang
        self.num_rolls = 2 if is_fang else 1
        self.atk_level = math.floor(118 * 1.2 + 8) # 8 is magic number from jamflex
        self.str_level = math.floor(118 * 1.23 + 8 + 3) # 3 is from attack style TODO
        self.def_level = math.floor(118 * 1.25 + 8)
        self.weapon_speed = 5 # ticks
        self.recoil = recoil
        self.justiciar = justiciar
        self.bf = bf
        
    def get_attack_roll_max(self):
        return self.atk_level * (self.slash_atk + 64)
    
    def get_attack_roll(self):
        return random.randint(0, self.get_attack_roll_max())
    
    def get_damage_roll(self):
        max_hit = math.floor((self.str_level * (self.str_bonus + 64) + 320) / 640)
        if not self.is_fang:
            return random.randint(0, max_hit)
        return random.randint(math.floor(.15 * max_hit), math.ceil(.85 * max_hit))
    
    def get_defence(self):
        return self.def_level

    def get_defence_roll_max(self):
        return (self.get_defence() + 9) * (self.slash_def + 64)
        
    def get_defence_roll(self):
        return random.randint(0, self.get_defence_roll_max())

    def get_bf_heal(self, damage):
        if random.randint(1,5) < 5:
            return 0
        return math.floor(damage * 3 / 10)

    def use_bf(self, damage):
        new_hp = self.current_hp + self.get_bf_heal(damage)
        if self.max_hp < new_hp:
            self.current_hp = self.max_hp
        else:
            self.current_hp = new_hp
    
        
class Monster:
    def __init__(self, hp, base_def, slash_def, defence_scaling: bool = False):
        self.max_hp = hp
        self.current_hp = hp
        self.base_def = base_def
        self.slash_def = slash_def
        self.defence_scaling = defence_scaling
        self.atk_level = 280
        self.slash_atk = 190
        self.base_str = 270
        self.num_rolls = 1
        self.atk_speed = 5
        
    def get_defence(self):
        if (self.defence_scaling):
            return self.base_def - math.floor((self.max_hp - self.current_hp) / 10)
        return self.base_def
    
    def get_defence_roll_max(self):
        return (self.get_defence() + 9) * (self.slash_def + 64)
        
    def get_defence_roll(self):
        return random.randint(0, self.get_defence_roll_max())
    
    def get_attack_roll_max(self):
        return self.atk_level * (self.slash_atk + 64)
    
    def get_attack_roll(self):
        return random.randint(0, self.get_attack_roll_max())

    def get_strength(self):
        if (self.defence_scaling):
            return self.base_str + math.floor((self.max_hp - self.current_hp)/self.max_hp * 90)
        return self.base_str

    def get_damage_roll(self):
        max_hit = math.floor(((self.get_strength() + 9) * (10 + 64) + 320) / 640)
        return math.floor(random.randint(0, max_hit) / 4)

def hit(player: Player, monster: Monster):
    def_roll = monster.get_defence_roll()
    for i in range(0, player.num_rolls):
        if player.get_attack_roll() > def_roll:
            return True
    return False

def fight(p: Player, m: Monster):
    hit_attempts = 0
    food_eats = 0
    total_dmg_taken = 0
    next_player_attack_tick = p.weapon_speed
    next_monster_attack_tick = m.atk_speed
    tick = 0
    bf_charges = 0
    
    while m.current_hp > 0:
        if tick == next_player_attack_tick:
            hit_attempts += 1
            if hit(p, m):
                damage = p.get_damage_roll()
                m.current_hp -= p.get_damage_roll()
                if p.bf:
                    p.use_bf(damage)
                    bf_charges += 1
            next_player_attack_tick += p.weapon_speed
        elif p.current_hp <= 30:
            p.current_hp += 20 # eat a shark 
            next_player_attack_tick += 3
            food_eats += 1
        if tick == next_monster_attack_tick:
            if hit(m, p):
                dmg = m.get_damage_roll()
                if p.justiciar:
                    reduction = math.ceil(dmg * p.slash_def / 3000)
                    dmg -= reduction
                total_dmg_taken += dmg
                p.current_hp -= dmg
                m.current_hp += math.floor(dmg / 2)
                if p.recoil:
                    m.current_hp -= 1
            next_monster_attack_tick += m.atk_speed
        tick += 1
    
    seconds_to_kill = tick * .6
    return seconds_to_kill, hit_attempts, food_eats, total_dmg_taken, bf_charges

NUM_SIMS = 5000
# df = pd.DataFrame([fight(Player(141, 343, 156, True, False, True), Monster(700, 215, 65, True)) for i in range(0, NUM_SIMS)])

def main():
    results = []
    for i in range(0,NUM_SIMS):
        player = Player(141, 343, 156, True, False, True, True)
        monster = Monster(700, 215, 65, True)
        results.append(fight(player, monster))
    ttk = statistics.mean([res[0] for res in results])
    food_eats = statistics.mean([res[2] for res in results])
    dmg_taken = statistics.mean([res[3] for res in results])
    bf_charges = statistics.mean([res[4] for res in results])
    print(f"ttk: {ttk}")
    print(f"food: {food_eats}")
    print(f"dmg: {dmg_taken}")
    print(f"bf: {bf_charges}")


if __name__ == "__main__":
    main()
