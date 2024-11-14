import torch
import random
import numpy as np
from collections import deque
from game import CarGameAI
from model import Linear_QNet, QTrainer
from plot import plot

MAX_MEMORY = 100_000  # Maximum memory size for replay buffer
BATCH_SIZE = 500
LR = 0.001


# Agent class responsible for interacting with the environment
class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # Exploration rate (for epsilon-greedy strategy)
        self.gamma = 0.9  # Discount factor
        self.memory = deque(maxlen=MAX_MEMORY)  # Experience replay memory
        self.model = Linear_QNet(9, 100, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    # Get the current state of the game
    def get_state(self, game):
        state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        if game.car.x > game.player.x + game.player.width:  # Car is to the right of player
            state[0] = 1
        if game.car.x + game.car.width < game.player.x:  # Car is to the left of player
            state[1] = 1
        if game.player.x < 4:  # Player is too far left
            state[2] = 1
        if game.player.x + game.player.width > 396:  # Player is too far right
            state[3] = 1
        if game.car.x + game.car.width >= 399 - game.player.width:  # Not enough space on the right
            state[4] = 1
        if game.car.x + game.car.width >= 399 - game.player.width and game.player.x + game.player.width >= game.car.x:
            state[5] = 1
        if game.car.x <= 1 + game.player.width:  # Not enough space on the left
            state[6] = 1
        if game.car.x <= 1 + game.player.width and game.player.x <= game.car.x + game.car.width:
            state[7] = 1
        if game.car.x + game.car.width > game.player.x and game.car.x < game.player.x + game.player.width:
            state[8] = 1  # Potential collision
        return state

    # Store the experience in the replay memory
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    # Train using a batch of experiences from the memory (long-term memory)
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    # Train using the most recent experience (short-term memory)
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    # Get the action for the current state using epsilon-greedy policy
    def get_action(self, state):
        self.epsilon = 50 - self.n_games  # Decrease exploration over time
        final_move = [0, 0, 0]
        if random.randint(0, 50) < self.epsilon:  # Random action (exploration)
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)  # Predict the action values
            move = torch.argmax(prediction).item()  # Choose the action with highest Q value
            final_move[move] = 1

        return final_move


# Train the agent
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = CarGameAI()
    while True:
        state_old = agent.get_state(game)  # Get the current state of the game
        final_move = agent.get_action(state_old)  # Get move

        # Perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        # If the game is over
        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            # Plot result
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

        if agent.n_games > 51:
            break


if __name__ == '__main__':
    train()
