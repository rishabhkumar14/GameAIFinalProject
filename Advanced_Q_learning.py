import time
import pickle
import numpy as np
from vis_gym import *
import random
from collections import defaultdict, deque

gui_flag = True
setup(GUI=gui_flag)
env = game  
env.render()

def hash(obs):
    """Convert observation to a hashable state"""
    x, y = obs['player_position']
    h = obs['player_health']
    g = obs['guard_in_cell']
    if not g:
        g = 0
    else:
        g = int(g[-1])
    return x * (5 * 3 * 5) + y * (3 * 5) + h * 5 + g

def Advanced_Q_learning(env, num_training_episodes=2000):
    # Define actions and initialize Q-table
    actions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'FIGHT', 'HIDE']
    Q = defaultdict(lambda: np.zeros(6))
    
    # Training parameters
    alpha, gamma, epsilon = 0.1, 0.95, 1.0
    epsilon_decay, min_epsilon = 0.995, 0.01
    
    # Precompute valid moves to avoid walls
    valid_moves = {}
    for x in range(5):
        for y in range(5):
            valid = []
            if x > 0: valid.append(0)  # UP
            if x < 4: valid.append(1)  # DOWN
            if y > 0: valid.append(2)  # LEFT
            if y < 4: valid.append(3)  # RIGHT
            valid.extend([4, 5])       # FIGHT and HIDE always valid
            valid_moves[(x, y)] = valid
    
    # Training loop
    print("\n=== Training Agent ===")
    wins = 0
    
    for episode in range(num_training_episodes):
        observation, _, done, _ = env.reset()
        state = hash(observation)
        total_reward = 0
        steps = 0
        
        # Track visited positions for cycle detection
        visited_positions = set()
        position_history = deque(maxlen=10)
        
        if episode % 50 == 0:
            win_rate = (wins / max(1, episode)) * 100 if episode > 0 else 0
            print(f"Episode {episode}/{num_training_episodes}, Win rate: {win_rate:.1f}%, Epsilon: {epsilon:.4f}")
        
        while not done and steps < 100:
            position = observation['player_position']
            guard_present = observation['guard_in_cell'] is not None
            
            # Track position history
            position_history.append(position)
            visited_positions.add(position)
            
            # Choose action (epsilon-greedy)
            valid_actions = valid_moves[position]
            
            if random.random() < epsilon:
                # Exploration with smart biases
                if guard_present:
                    # Choose FIGHT or HIDE based on health
                    weights = [0.7, 0.3] if observation['player_health'] == 2 else [0.3, 0.7]
                    action_idx = random.choices([4, 5], weights=weights)[0]
                else:
                    # Bias toward goal with cycle avoidance
                    x, y = position
                    goal_x, goal_y = env.goal_room
                    weights = [1.0] * 6
                    
                    # Increase weights for directions toward goal
                    if 0 in valid_actions and x > goal_x: weights[0] = 3.0  # UP
                    if 1 in valid_actions and x < goal_x: weights[1] = 3.0  # DOWN
                    if 2 in valid_actions and y > goal_y: weights[2] = 3.0  # LEFT
                    if 3 in valid_actions and y < goal_y: weights[3] = 3.0  # RIGHT
                    
                    # Avoid cycles by reducing weight of return direction
                    if len(position_history) >= 3 and position_history.count(position) >= 2:
                        last_idx = -2
                        while last_idx >= -len(position_history) and position_history[last_idx] == position:
                            last_idx -= 1
                        
                        if last_idx >= -len(position_history):
                            prev_x, prev_y = position_history[last_idx]
                            if prev_x < x: weights[0] = 0.1      # Don't go UP
                            elif prev_x > x: weights[1] = 0.1    # Don't go DOWN
                            elif prev_y < y: weights[2] = 0.1    # Don't go LEFT
                            elif prev_y > y: weights[3] = 0.1    # Don't go RIGHT
                    
                    # Limit to valid actions
                    valid_weights = [weights[i] if i in valid_actions else 0.0 for i in range(6)]
                    action_idx = random.choices(range(6), weights=valid_weights)[0] if sum(valid_weights) > 0 else random.choice(valid_actions)
            else:
                # Exploitation: choose best valid action
                q_values = Q[state]
                
                if guard_present:
                    # When guard present, only choose between FIGHT and HIDE
                    action_idx = 4 if q_values[4] >= q_values[5] else 5
                else:
                    # Mask invalid actions
                    masked_q = np.copy(q_values)
                    for i in range(6):
                        if i not in valid_actions:
                            masked_q[i] = -np.inf
                    action_idx = np.argmax(masked_q)
            
            # Take action
            next_observation, reward, done, info = env.step(action_idx)
            next_state = hash(next_observation)
            
            # Reward shaping
            if not done and not guard_present:
                # Calculate distances to goal
                curr_x, curr_y = position
                next_x, next_y = next_observation['player_position']
                goal_x, goal_y = env.goal_room
                
                curr_dist = abs(curr_x - goal_x) + abs(curr_y - goal_y)
                next_dist = abs(next_x - goal_x) + abs(next_y - goal_y)
                
                # Reward progress toward goal, penalize cycles
                if next_dist < curr_dist:
                    reward += 0.5
                if tuple(next_observation['player_position']) in visited_positions:
                    reward -= 0.3
            
            # Q-learning update
            best_next_q = np.max(Q[next_state])
            td_target = reward + gamma * best_next_q
            Q[state][action_idx] += alpha * (td_target - Q[state][action_idx])
            
            # Update state
            observation = next_observation
            state = next_state
            total_reward += reward
            steps += 1
            
            # Render occasionally
            if episode % 100 == 0 and gui_flag:
                refresh(observation, reward, done, info, delay=0.05)
        
        # Update statistics and decay exploration
        if done and total_reward > 0:
            wins += 1
        epsilon = max(min_epsilon, epsilon * epsilon_decay)
    
    print(f"\nTraining completed: {wins} successful episodes ({(wins/num_training_episodes)*100:.1f}%)")
    
    # Play demonstration episodes
    
    # Convert defaultdict to regular dict for saving
    q_table_dict = {state: values.tolist() for state, values in Q.items()}
    return q_table_dict

# Uncomment to train a new agent
# Q_table = Advanced_Q_learning(env, num_training_episodes=2000)
# with open('advanced_Q_table.pickle', 'wb') as handle:
#     pickle.dump(Q_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
# print("Q-table saved to 'advanced_Q_table.pickle'")


def test_agent():
    try:
        Q_table = np.load('advanced_Q_table.pickle', allow_pickle=True)
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

# # Test existing agent
test_agent()

# Close environment
env.close()