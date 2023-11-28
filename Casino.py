import numpy as np

class Casino:
    def __init__(self, host_reward, bet_lower_limit, bet_upper_limit) -> None:
        self.host_reward = host_reward
        self.bet_upper_limit = bet_upper_limit
        self.bet_lower_limit = bet_lower_limit

    def bet(self, player_amount:int, opponent_amount:int, player_choice:int, opponent_choice:int):
        if player_choice == 1 and opponent_choice == 0:
            return opponent_amount, -opponent_amount
        
        if player_choice == 0 and opponent_choice == 1:
            return -player_amount, player_amount
        
        if player_choice == 0 and opponent_choice == 0:
            return self.host_reward, self.host_reward
        
        if player_choice == 1 and opponent_choice == 1:
            return - player_amount + player_amount // 2, - opponent_amount + opponent_amount // 2


class Agent:
    def __init__(self, money, casino:Casino) -> None:
        self.money = money
        self.casino = casino

    def get_money(self):
        return self.money
    
    def get_availiable_bets(self):
        return [i for i in range(1, self.money + 1) if i <= self.casino.bet_upper_limit and i >= self.casino.bet_lower_limit]
    
    def update_money(self, gain:int):
        self.money += gain

class Player(Agent):
    def __init__(self, money, casino:Casino) -> None:
        super().__init__(money, casino=casino)

class BraggerAgent(Agent):
    def __init__(self, casino:Casino) -> None:
        super().__init__(10, casino=casino)

    def get_bet(self, player_bet:int):
        return player_bet
    
    def get_choice(self, player_bet:int):
        return 1
    
    def get_description(self):
        desc = f"You overheard that this guy is a bragger. He always bets high.\n"
        return desc

class CowardAgent(Agent):
    def __init__(self, casino:Casino) -> None:
        super().__init__(10, casino=casino)

    def get_bet(self, player_bet:int):
        return player_bet
    
    def get_choice(self, player_bet:int):
        return 0
    
    def get_description(self):
        desc = f"You overheard that this guy is a coward. He always bets low.\n"
        return desc
    
class RandomAgent(Agent):
    def __init__(self, casino:Casino) -> None:
        super().__init__(10,casino=casino)

    def get_bet(self, player_bet:int):
        return player_bet
    
    def get_choice(self, player_bet:int):
        return np.random.choice([0, 1])
    
    def get_description(self):
        desc = f"You overheard that this guy is mad. He randomly bets high or low.\n"
        return desc

class SmartAgent(Agent):
    def __init__(self, casino:Casino) -> None:
        super().__init__(10, casino=casino)

    def get_bet(self, player_bet:int):
        return player_bet
    
    def gen_suspected_choice(self, player_bet:int):
        return np.random.choice([0, 1])

    def get_expected_reward(self, player_bet:int, choice:int, sim_iter:int = 200):
        expected_reward = 0

        for _ in range(sim_iter):
            _, reward = self.casino.bet(player_bet, self.get_bet(player_bet), self.gen_suspected_choice(player_bet), choice)
            expected_reward += reward

        return expected_reward / sim_iter

    def get_choice(self, player_bet:int):
        exp_high_reward = self.get_expected_reward(player_bet, 1)
        exp_low_reward = self.get_expected_reward(player_bet, 0)

        if exp_high_reward > exp_low_reward:
            return 1
        else:
            return 0
        
    def get_description(self):
        desc = f"This guy appears to be smart. He bets high if he thinks the expected reward is higher than betting low. And he assumes you choose randomly.\n"
        return desc
        

class Playthrough:
    def __init__(self, casino:Casino, player:Agent, opponents:list, with_html_emphasis:bool = False) -> None:
        self.casino = casino
        self.player = player
        self.opponents = opponents
        self.reward_trace = [{} for _ in range(len(opponents))]
        self.emphasis = ""
        self.emphasis_end = ""
        if with_html_emphasis:
            self.emphasis = "<b>"
            self.emphasis_end = "</b>"

    def get_intro_str(self):
        intro = "You walk into a casino with your last ten coins. " 
        intro += "These are all you have. "
        intro += "Low on budget, you know you can only rely on your intelligence. "
        intro += "With the last hope, you sit in front of a table…\n"
        intro += "\n"
        intro += "Rules:\n"
        intro += self.get_rules_str()
        intro += "\n"
        intro += self.get_money_str()
        intro += "Welcome to the casino game!\n"

        return intro

    def get_rules_str(self):

        rules = f"You and your opponent must bet the same amount between {self.emphasis}{self.casino.bet_lower_limit}{self.emphasis_end} to {self.emphasis}{self.casino.bet_upper_limit}{self.emphasis_end} coin(s) each round. You both simultaneously choose either {self.emphasis}\"High\"{self.emphasis_end} or {self.emphasis}\"Low\"{self.emphasis_end} as your betting option.\n"
        rules += f"1. If both players choose {self.emphasis}\"Low,\"{self.emphasis_end} the host adds {self.emphasis}{self.casino.host_reward}{self.emphasis_end} coin(s) to the pot for each side.\n"
        rules += f"2. If both players choose {self.emphasis}\"High,\"{self.emphasis_end} the host takes half of the coins from each side. {self.emphasis}For example, if you bet 3 coins, one coin is left.{self.emphasis_end}\n"
        rules += f"3. If one player selects {self.emphasis}\"High\"{self.emphasis_end} while the other chooses {self.emphasis}\"Low,\"{self.emphasis_end} the {self.emphasis}\"High\"{self.emphasis_end} player wins all the coins in the pot.\n"
        rules += f"4. Remember to take all your coins from the table before starting the next round.\n"
        
        return rules

    def get_money_str(self):
        return f"You have {self.emphasis}{self.player.get_money()}{self.emphasis_end} coin(s) left.\n"
    
    def get_bet_str(self):
        return f"You can bet {self.emphasis}{self.player.get_availiable_bets()}{self.emphasis_end} coin(s).\n"
    
    def get_reward_str(self, round_num:int):
        r = self.reward_trace[round_num]
        desc = ""
        if r["player_choice"] == 1 and r["opponent_choice"] == 1:
            desc = f"Host takes half of the coins from each side.\n"
        elif r["player_choice"] == 0 and r["opponent_choice"] == 0:
            desc = f"Host adds {self.emphasis}{self.casino.host_reward}{self.emphasis_end} coin(s) to the pot for each side.\n"
        if r["player_reward"] > 0:
            return desc + f"You won {self.emphasis}{r['player_reward']}{self.emphasis_end} coin(s).\n"
        elif r["player_reward"] < 0:
            return desc + f"You lost {self.emphasis}{-r['player_reward']}{self.emphasis_end} coin(s).\n"

    def get_choice_str(self, round_num:int):
        c = self.reward_trace[round_num]
        choice = "High" if c["player_choice"] == 1 else "Low"
        bet = c["player_bet"]
        return f"You bet {self.emphasis}{bet}{self.emphasis_end} coin(s) on {self.emphasis}{choice}{self.emphasis_end}.\n"

    def get_oppo_choice_str(self, round_num:int):
        c = self.reward_trace[round_num]
        choice = "High" if c["opponent_choice"] == 1 else "Low"
        bet = c["opponent_bet"]
        return f"Your opponent bet {self.emphasis}{bet}{self.emphasis_end} coin(s) on {self.emphasis}{choice}{self.emphasis_end}.\n"

    def get_rounds(self):
        return len(self.opponents)

    def get_round_str(self, round_num:int):
        desc = f"BEGIN: You are in round {self.emphasis}{round_num + 1}{self.emphasis_end}.\n"
        money_left = self.get_money_str()
        oppo_desc = f"You see your opponent." + self.emphasis + self.opponents[round_num].get_description() + self.emphasis_end
        bet_desc = self.get_bet_str()

        return desc + money_left + oppo_desc + "\n" +  bet_desc

    def play_round(self, round_num:int, player_bet:int, player_choice:int):
        agent = self.opponents[round_num]
        oppo_bet = agent.get_bet(player_bet)
        oppo_choice = agent.get_choice(player_bet)
        p_r, a_r = self.casino.bet(player_bet, oppo_bet, player_choice, oppo_choice)
        self.player.update_money(p_r)
        self.reward_trace[round_num] = {"player_bet": player_bet, "opponent_bet": oppo_bet, "player_choice":player_choice, "opponent_choice":oppo_choice, "player_reward":p_r, "opponent_reward":a_r}

    def get_round_result_str(self, round_num:int):
        return "RESULT: " + self.get_choice_str(round_num) + self.get_oppo_choice_str(round_num) + self.get_reward_str(round_num) + self.get_money_str()
    
    def compute_avg_gain(self, round_num:int, player_bet:int, player_choice:int):
        agent = self.opponents[round_num]

        max_iter = 300
        total_gain = 0
        for _ in range(max_iter):
            p_r, _ = self.casino.bet(player_bet, agent.get_bet(player_bet), player_choice, agent.get_choice(player_bet))
            total_gain += p_r

        return total_gain / max_iter