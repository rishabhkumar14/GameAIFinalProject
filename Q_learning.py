import time
import pickle
import numpy as np
from vis_gym import *

# Enable GUI visualization
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


def Q_learning(num_episodes=1000000, gamma=0.9, epsilon=1.0, decay_rate=0.999999):
    # Initialize Q-table as empty dictionary and update counter
    Q_table = {}  
    num_updates = np.zeros((375, 6)) 

    for episode in range(num_episodes):
        print(episode)
        # Reset environment for new episode
        obs, _, done, _ = env.reset()
        state = hash(obs)

        while not done:
            # Initialize Q-values for new states
            Q_table.setdefault(state, np.zeros(6))

            # Epsilon-greedy action selection
            if np.random.rand() < epsilon:
                # Exploration: choose random action
                action = env.action_space.sample()
            else:
                # Exploitation: choose best action according to Q-table
                action = np.argmax(Q_table[state])

            # Take action and observe next state and reward
            obs_next, reward, done, info = env.step(action)
            next_state = hash(obs_next)
            Q_table.setdefault(next_state, np.zeros(6))

            # Calculate learning rate that decreases with visits
            eta = 1.0 / (1 + num_updates[state, action])
            
            # Q-learning update equation
            Q_table[state][action] = (1 - eta) * Q_table[state][action] + eta * (reward + gamma * np.max(Q_table[next_state]))

            # Track number of updates for this state-action pair
            num_updates[state, action] += 1
            state = next_state

            # Update visualization if GUI enabled
            if gui_flag:
                refresh(obs_next, reward, done, info)
 
        # Decay exploration rate after each episode
        epsilon = max(epsilon*decay_rate, 0.01)

    return Q_table

# Uncomment to train a new agent
# Q_table = Q_learning(num_episodes=1000000, gamma=0.9, epsilon=1, decay_rate=0.999999) # Run Q-learning
# with open('Q_table.pickle', 'wb') as handle:
#     pickle.dump(Q_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
# print("Q-table saved to 'Q_table.pickle'")


def test_agent():
    """Test a pre-trained Q-learning agent"""
    try:
        # Load saved Q-table
        Q_table = np.load('Q_table.pickle', allow_pickle=True)
        obs, reward, done, info = env.reset()
        total_reward = 0
        
        # Run agent until episode ends
        while not done:
            # Get state and choose best action from Q-table
            state = hash(obs)
            action = np.argmax(Q_table[state])
            
            # Take action and update total reward
            obs, reward, done, info = env.step(action)
            total_reward += reward
            
            # Update visualization if GUI enabled
            if gui_flag:
                refresh(obs, reward, done, info)  # Update the game screen [GUI only]
                
        print("Total reward:", total_reward)
        
        # Report result
        print(f"Test complete: {'SUCCESS' if total_reward > 0 else 'FAILURE'}")
        print(f"Total reward: {total_reward}")
    
    except FileNotFoundError:
        print("No advanced_Q_table.pickle file found. Run the training code first.")
    except Exception as e:
        print(f"Error loading or testing agent: {e}")

# Test the pre-trained agent
test_agent()

# Close the environment when done
env.close()