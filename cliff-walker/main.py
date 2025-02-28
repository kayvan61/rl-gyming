import gymnasium as gym
import matplotlib.pyplot as plt
import random

class CliffWalker:
    def __init__(self, n_actions, n_states, learning_rate, discount):
        self.tab = [[0]*n_actions for _ in range(n_states)]
        self.n_tab = [0]*n_states
        self.lr = learning_rate
        self.gamma = discount

    def get_action(self, state):
        res = self.tab[state]
        best_act = 0
        for i, val in enumerate(res):
            if res[best_act] < val:
                best_act = i
        return best_act

    def reward(self, old_state, action, reward, next_state):
        s = old_state
        a = action
        self.tab[s][a] += self.lr * (reward + self.gamma*(max(self.tab[next_state]) - self.tab[s][a]))

    def reward_SARSA(self, old_state, action, reward, next_state):
        # sarsa will grab best from policy action
        s = old_state
        a = action
        next_action = self.get_action(next_state)
        self.tab[s][a] += self.lr * (reward + self.gamma*self.tab[next_state][next_action] - self.tab[s][a])

    def reward_TD(self, old_state, action, reward, next_state):
        s = old_state
        a = action
        next_state_value = max(self.tab[next_state])
        self.n_tab[old_state] += 1
        self.tab[s][a] += 1/(self.n_tab[old_state]) * (reward + self.gamma*next_state_value - self.tab[s][a])

def runner(train_steps, eval_steps):
    env = gym.make("CliffWalking-v0", is_slippery=False)#, render_mode="human")
    cw = CliffWalker(4, 48, .8, .6)
    
    observation, info = env.reset(seed=42)
    action = cw.get_action(observation)

    # train the TD values with a random walker
    TRAIN_STEP_COUNT = train_steps
    for _ in range(TRAIN_STEP_COUNT):
        new_observation, reward, terminated, truncated, info = env.step(action)
    
        if terminated or truncated:
            observation, info = env.reset()
        cw.reward_SARSA(observation, action, reward, new_observation)
        observation = new_observation
        action = cw.get_action(observation)

    print("\n".join([str(i) + ": " + str(x) for i, x in enumerate(cw.tab)]))

    # eval the training done in the last step
    env.reset()
    EVAL_STEP_COUNT = eval_steps
    observation, info = env.reset(seed=42)
    action = cw.get_action(observation)
    steps = 0
    wins = []
    for _ in range(EVAL_STEP_COUNT):
        new_observation, reward, terminated, truncated, info = env.step(action)
    
        if terminated or truncated:
            observation, info = env.reset()
            wins.append(steps)
            steps = 0
        steps += 1
        #cw.reward_TD(observation, action, reward, new_observation)
        observation = new_observation
        action = cw.get_action(observation)

    env.close()

    print(f"train: {TRAIN_STEP_COUNT} eval: {EVAL_STEP_COUNT}", end=' ')
    if len(wins) > 0:
        print(f"won in {sum(wins)/len(wins)} steps on average")
    else:
        print("never won!")

steps = [10**i for i in range(10)][4:5]
for x in steps:
    runner(x,10000)
    
