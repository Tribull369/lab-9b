#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 11:31:59 2024

@author: benzhang
"""

"""
Simple implementation of the Schelling model of segregation in Python
(https://www.uzh.ch/cmsssl/suz/dam/jcr:00000000-68cb-72db-ffff-ffffff8071db/04.02%7B_%7Dschelling%7B_%7D71.pdf)
For use in classes at the Harris School of Public Policy
"""

from numpy import random, mean

# Update out_path to point to somewhere on your computer
params = {'world_size': (10, 10),
          'num_agents': 10,
          'same_pref': 0.4,
          'max_iter': 10,
          'out_path': r'/Users/benzhang/Documents/GitHub/lab-9b/abm_results.csv' }

class Agent:
    def __init__(self, world, kind, same_pref):
        self.world = world
        self.kind = kind
        self.same_pref = same_pref
        self.location = None

    def move(self):
        happy = self.am_i_happy()
        if not happy:
            vacancies = self.world.find_vacant()
            if not vacancies:
                return 2  # No vacant spots
            for patch in vacancies:
                if self.am_i_happy(loc=patch):
                    self.world.grid[self.location] = None
                    self.location = patch
                    self.world.grid[patch] = self
                    return 1
            return 2
        return 0

    def am_i_happy(self, loc=None):
        if loc is None:
            loc = self.location
        neighbors = self.locate_neighbors(loc)
        neighbor_agents = [self.world.grid[patch] for patch in neighbors]
        same_kind = sum(agent.kind == self.kind for agent in neighbor_agents if agent)
        total_neighbors = sum(1 for agent in neighbor_agents if agent)
        if total_neighbors == 0:
            return False
        return same_kind / total_neighbors >= self.same_pref

    def locate_neighbors(self, loc):
        x, y = loc
        neighbors = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0)]
        x_max, y_max = self.world.params['world_size']
        return [(nx % x_max, ny % y_max) for nx, ny in neighbors]

class World:
    def __init__(self, params):
        self.params = params
        self.grid = self.build_grid(params['world_size'])
        self.agents = self.build_agents(params['num_agents'], params['same_pref'])
        self.init_world()

    def build_grid(self, world_size):
        return {(x, y): None for x in range(world_size[0]) for y in range(world_size[1])}

    def build_agents(self, num_agents, same_pref):
        kinds = ['red', 'blue'] * (num_agents // 2)
        agents = [Agent(self, kind, same_pref) for kind in kinds]
        random.shuffle(agents)
        return agents

    def init_world(self):
        for agent in self.agents:
            loc = self.find_vacant(single=True)
            if loc is not None:
                self.grid[loc] = agent
                agent.location = loc

    def find_vacant(self, single=False):
        empties = [loc for loc, occupant in self.grid.items() if occupant is None]
        if not empties:
            return None if single else []
        return random.choice(empties) if single else empties

    def run(self):
        for iteration in range(self.params['max_iter']):
            random.shuffle(self.agents)
            move_results = [agent.move() for agent in self.agents]
            if all(result == 0 for result in move_results):
                print(f'Everyone is happy! Stopping after iteration {iteration}.')
                break
            if all(result != 1 for result in move_results):
                print(f'Some agents are unhappy, but they cannot move. Stopping after iteration {iteration}.')
                break
        self.report()

    def report(self):
        happy_count = sum(agent.am_i_happy() for agent in self.agents)
        print(f'Total happy agents: {happy_count}/{len(self.agents)}')

world = World(params)
world.run()
