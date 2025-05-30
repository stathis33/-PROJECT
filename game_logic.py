import math

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.roads = []

class Road:
    def __init__(self, owner, start_pos, end_pos):
        self.owner = owner
        self.start_pos = start_pos
        self.end_pos = end_pos

class Game:
    def __init__(self):
        self.players = []
        self.roads = []

    def get_longest_road_owner(self):
        max_length = 0
        owner = None
        for player in self.players:
            visited = set()
            for road in player.roads:
                length = self.dfs_road_length(road, player, visited, set())
                if length > max_length:
                    max_length = length
                    owner = player
        return owner

    def dfs_road_length(self, current_road, player, visited, path):
        road_id = (current_road.start_pos, current_road.end_pos)
        if road_id in path:
            return 0
        path.add(road_id)

        max_branch = 0
        for road in player.roads:
            if road == current_road:
                continue
            if (self.is_close(road.start_pos, current_road.start_pos) or
                self.is_close(road.start_pos, current_road.end_pos) or
                self.is_close(road.end_pos, current_road.start_pos) or
                self.is_close(road.end_pos, current_road.end_pos)):
                max_branch = max(max_branch, self.dfs_road_length(road, player, visited, path.copy()))
        return 1 + max_branch

    def is_close(self, pos1, pos2, threshold=0.01):
        return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1]) < threshold
