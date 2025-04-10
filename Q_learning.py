import time
import pickle
import numpy as np
from game.vis_gym import *




gui_flag = True
setup(GUI=gui_flag)
env = game  
env.render()

def hash(obs):
    x, y = obs['player_position']
    h = obs['player_health']
    g = obs['guard_in_cell']
    if not g:
        g = 0
    else:
        g = int(g[-1])
    return x * (5 * 3 * 5) + y * (3 * 5) + h * 5 + g

def Q_learning(num_episodes=100000, gamma=0.9, epsilon=1.0, decay_rate=0.999999):
    Q_table = {}  
    num_updates = np.zeros((375, 6)) 

    for episode in range(num_episodes):
        print(episode)
        obs, _, done, _ = env.reset()
        state = hash(obs)

        while not done:
            Q_table.setdefault(state, np.zeros(6))

            if np.random.rand() < epsilon:
                action = env.action_space.sample()
            else:
                action = np.argmax(Q_table[state])

            obs_next, reward, done, info = env.step(action)
            next_state = hash(obs_next)
            Q_table.setdefault(next_state, np.zeros(6))

            eta = 1.0 / (1 + num_updates[state, action])
            Q_table[state][action] = (1 - eta) * Q_table[state][action] + eta * (reward + gamma * np.max(Q_table[next_state]))

            num_updates[state, action] += 1
            state = next_state

            if gui_flag:
                refresh(obs_next, reward, done, info)
 
        epsilon = max(epsilon*decay_rate, 0.01)

    return Q_table

# Uncomment to train a new agent
# Q_table = Q_learning(num_episodes=1000000, gamma=0.9, epsilon=1, decay_rate=0.999999) # Run Q-learning
# with open('Q_table.pickle', 'wb') as handle:
#     pickle.dump(Q_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
# print("Q-table saved to 'Q_table.pickle'")


def test_agent():
    try:
        Q_table = np.load('Q_table.pickle', allow_pickle=True)
        obs, reward, done, info = env.reset()
        total_reward = 0
        while not done:
            state = hash(obs)
            action = np.argmax(Q_table[state])
            obs, reward, done, info = env.step(action)
            total_reward += reward
            if gui_flag:
                refresh(obs, reward, done, info)  # Update the game screen [GUI only]
        print("Total reward:", total_reward)
        
        # Result
        print(f"Test complete: {'SUCCESS' if total_reward > 0 else 'FAILURE'}")
        print(f"Total reward: {total_reward}")
    
    except FileNotFoundError:
        print("No advanced_Q_table.pickle file found. Run the training code first.")
    except Exception as e:
        print(f"Error loading or testing agent: {e}")

# Uncomment to test the agent
test_agent()

# Close the environment when done
env.close()