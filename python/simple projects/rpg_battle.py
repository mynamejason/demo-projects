# A very simple RPG battle system
# Fight against Generic Bad Guy

import random

class Actors:
    def __init__(self, name, health = int, special = int, attacks = []):
        self.name = name
        self.health = health
        self.special = special
        self.attacks = attacks # Attacks will be a list

    def attack_list(self, attacks):
        match attacks:
            case "attack":
                return 1
            case "heal":
                return 2
            case "fireball":
                return 3
            case _:
                return 0

class Player(Actors):
    health = 100 # default HP
    special = 10 # default Special/MP

    def use_choice(self, choice):
        choice_lowercase = choice.lower()
        if choice not in self.attacks:
            print("Invalid Choice!")
            return -1
        else:
           selected = self.attack_list(choice_lowercase)
           match selected:
               case 1:
                   print("You attacked with your sword!")
                   return random.randint(10, 20)
               case 2:
                   if self.special > 0:
                    print("You healed using magic!")
                    self.special -= 1
                    self.health += random.randint(20, 30)
                    return 0
                   else:
                    print("Not enough Special Points!")
                    return -1
               case 3:
                   if self.special > 1:
                    print("You blasted the enemy with a fireball!")
                    self.special -= 2
                    return random.randint(40, 50)
                   else:
                    print("Not enough Special Points!")
                    return -1
                    

class Bad_Guy(Actors):
    def attack_choice(self):
        i = random.randrange(0, len(self.attacks))
        choice = self.attacks[i].lower()
        result = self.attack_list(choice)
        match result:
            case 1:
                print("The bad guy attacks!")
                return random.randint(5, 10)
            case 3:
                if self.special < 2:
                    return self.attack_choice()
                else:
                    print("The bad guy blasted you with a fireball!")
                    self.special -= 2
                    return random.randint(10, 20)

def battle_system():
    player = Player("Player", 100, 10, ['Attack', 'Heal', 'Fireball'])
    enemy = Bad_Guy("Bad Guy", 300, 10, ['Attack', 'Fireball'])

    print("A bad guy appeared!")

    while player.health > 0:
        print("Player's HP: {fPlayerHP}\nPlayer's Special: {fPlayerSP}\nEnemy's HP: {fEnemyHP}\nEnemy's SP: {fEnemySP}".format(fPlayerHP = player.health, fPlayerSP = player.special, fEnemyHP = enemy.health, fEnemySP = enemy.special))
        # Player's turn
        player_choice = input("What will you do? {list}\n".format(list=player.attacks)).capitalize()
        player_damage = player.use_choice(player_choice)
        if player_damage < 0:
            continue
        enemy.health -= player_damage

        # Enemy's turn
        if enemy.health <= 0:
            break
        enemy_damage = enemy.attack_choice()
        player.health -= enemy_damage

    if player.health <= 0:
        print("You took mortal damage...")
        print("Game Over...")
    else:
        print ("The enemy took mortal damage!")
        print("You Win!")
    
    return 0

battle_system()