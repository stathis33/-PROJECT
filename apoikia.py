import random
import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Build Your Colony")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PLAYER_COLORS = [(255, 0, 0), (0, 0, 255), (0, 200, 0), (255, 165, 0)]

# Hexagon settings
TILE_RADIUS = 40

class Player:
    def __init__(self, name, color, is_ai=False):
        self.name = name
        self.color = color
        self.is_ai = is_ai
        self.resources = {'wood': 0, 'brick': 0, 'wheat': 0, 'sheep': 0, 'ore': 0}
        self.settlements = []
        self.roads = []
        self.points = 0

class Tile:
    def __init__(self, resource_type, number, position):
        self.resource_type = resource_type
        self.number = number
        self.blocked = False
        self.position = position
        self.vertices = self.calculate_vertices()
        self.settlements = []

    def calculate_vertices(self):
        x, y = self.position
        vertices = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            point_x = x + TILE_RADIUS * math.cos(angle_rad)
            point_y = y + TILE_RADIUS * math.sin(angle_rad)
            vertices.append((point_x, point_y))
        return vertices

class Settlement:
    def __init__(self, owner, location):
        self.owner = owner
        self.location = location

class Road:
    def __init__(self, owner, start_pos, end_pos):
        self.owner = owner
        self.start_pos = start_pos
        self.end_pos = end_pos

class Game:
    def __init__(self):
        self.players = []
        self.tiles = []
        self.roads = []
        self.current_player_index = 0
        self.last_roll = None
        self.building_road = False
        self.setup_tiles()

    def setup_tiles(self):
        resources = ['wood', 'wheat', 'ore', 'brick', 'sheep', 'wheat', 'brick', 'ore', 'wheat',
                     'brick', 'wheat', 'wood', 'sheep', 'wood', 'wood', 'sheep', 'sheep', 'ore']
        numbers = [5, 3, 2, 12, 5, 6, 4, 8, 4, 11, 7, 9, 8, 9, 12, 10, 11, 10]
        x_offset = TILE_RADIUS * math.sqrt(3)
        y_offset = TILE_RADIUS * 1.5
        rows = [3, 4, 5, 4, 3]
        start_y = 100
        idx = 0
        for row_idx, tiles_in_row in enumerate(rows):
            start_x = WIDTH/2 - (tiles_in_row - 1) * x_offset / 2
            for tile_in_row in range(tiles_in_row):
                if idx >= len(resources):
                    break
                x = start_x + tile_in_row * x_offset
                y = start_y + row_idx * y_offset
                self.tiles.append(Tile(resources[idx], numbers[idx], (x, y)))
                idx += 1

    def add_player(self, name, is_ai=False):
        color = PLAYER_COLORS[len(self.players) % len(PLAYER_COLORS)]
        self.players.append(Player(name, color, is_ai))

    def draw_hexagon(self, surface, color, position, radius):
        x, y = position
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            point_x = x + radius * math.cos(angle_rad)
            point_y = y + radius * math.sin(angle_rad)
            points.append((point_x, point_y))
        pygame.draw.polygon(surface, color, points, 2)

    def draw_tiles(self):
        for tile in self.tiles:
            self.draw_hexagon(screen, BLACK, tile.position, TILE_RADIUS)
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"{tile.number}", True, BLUE)
            text_rect = text.get_rect(center=tile.position)
            screen.blit(text, text_rect)
            resource_font = pygame.font.SysFont(None, 18)
            resource_text = resource_font.render(tile.resource_type, True, GREEN)
            resource_rect = resource_text.get_rect(center=(tile.position[0], tile.position[1] + 20))
            screen.blit(resource_text, resource_rect)
            for settlement in tile.settlements:
                pygame.draw.circle(screen, settlement.owner.color, settlement.location, 8)

    def draw_roads(self):
        for road in self.roads:
            pygame.draw.line(screen, road.owner.color, road.start_pos, road.end_pos, 5)

    def is_close(self, pos1, pos2, threshold=10):
        return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1]) < threshold

    def place_settlement(self, pos):
        for tile in self.tiles:
            for vertex in tile.vertices:
                dist = math.hypot(pos[0] - vertex[0], pos[1] - vertex[1])
                if dist < 10:
                    for other_tile in self.tiles:
                        for settlement in other_tile.settlements:
                            if self.is_close(vertex, settlement.location, threshold=55):
                                print("Too close to another settlement!")
                                return

                    player = self.players[self.current_player_index]

                    # Αν είναι το 3ο ή επόμενο σπίτι, αφαιρούμε πόρους
                    if len(player.settlements) >= 2:
                        if (player.resources['wood'] >= 1 and player.resources['brick'] >= 1 and
                            player.resources['sheep'] >= 1 and player.resources['wheat'] >= 1):
                            player.resources['wood'] -= 1
                            player.resources['brick'] -= 1
                            player.resources['sheep'] -= 1
                            player.resources['wheat'] -= 1
                        else:
                            print("Δεν έχεις αρκετούς πόρους για να χτίσεις σπίτι!")
                            return

                    settlement = Settlement(player, vertex)
                    tile.settlements.append(settlement)
                    player.settlements.append(settlement)
                    print(f"Settlement placed by {player.name}")
                    self.current_player_index = (self.current_player_index + 1) % len(self.players)
                    return

    def place_road(self, pos):
        min_dist = float('inf')
        best_start = None
        best_end = None
        for tile in self.tiles:
            vertices = tile.vertices
            for i in range(6):
                start = vertices[i]
                end = vertices[(i+1)%6]
                mid_x = (start[0] + end[0]) / 2
                mid_y = (start[1] + end[1]) / 2
                dist = math.hypot(pos[0] - mid_x, pos[1] - mid_y)
                if dist < min_dist:
                    min_dist = dist
                    best_start = start
                    best_end = end

        if min_dist < 20:
            player = self.players[self.current_player_index]

            for road in self.roads:
                if (road.start_pos == best_start and road.end_pos == best_end) or (road.start_pos == best_end and road.end_pos == best_start):
                    print("Υπάρχει ήδη δρόμος εδώ!")
                    return

            connected = False

            if len(player.roads) < 2:
                for settlement in player.settlements[:2]:
                    if self.is_close(settlement.location, best_start) or self.is_close(settlement.location, best_end):
                        connected = True
                        break
                if not connected:
                    print("Ο πρώτος δρόμος πρέπει να συνδέεται με το αρχικό σπίτι!")
                    return
            else:
                for road in player.roads:
                    if (self.is_close(road.start_pos, best_start) or self.is_close(road.end_pos, best_start)) or \
                       (self.is_close(road.start_pos, best_end) or self.is_close(road.end_pos, best_end)):
                        connected = True
                        break
                for settlement in player.settlements:
                    if self.is_close(settlement.location, best_start) or self.is_close(settlement.location, best_end):
                        connected = True
                        break
                if not connected:
                    print("Δεν συνδέεται με υπάρχοντα δρόμο ή οικισμό!")
                    return

            if len(player.roads) >= 2:
                if player.resources['wood'] < 1 or player.resources['brick'] < 1:
                    print("Not enough resources to build a road!")
                    return
                player.resources['wood'] -= 1
                player.resources['brick'] -= 1

            new_road = Road(player, best_start, best_end)
            self.roads.append(new_road)
            player.roads.append(new_road)
            print(f"Road built by {player.name}")
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def roll_dice(self):
        self.last_roll = random.randint(1, 6) + random.randint(1, 6)
        print(f"Dice rolled: {self.last_roll}")
        self.distribute_resources()

    def distribute_resources(self):
        for player in self.players:
            for settlement in player.settlements:
                for tile in self.tiles:
                    if tile.number == self.last_roll:
                        for vertex in tile.vertices:
                            if math.hypot(settlement.location[0] - vertex[0], settlement.location[1] - vertex[1]) < 10:
                                player.resources[tile.resource_type] += 1
                                print(f"{player.name} receives 1 {tile.resource_type}")
                                break

    def draw_ui(self):
        font = pygame.font.SysFont(None, 36)
        roll_text = font.render("Roll Dice", True, BLACK)
        pygame.draw.rect(screen, YELLOW, (WIDTH-150, HEIGHT-100, 120, 50))
        screen.blit(roll_text, (WIDTH-145, HEIGHT-90))
        if self.last_roll is not None:
            result_text = font.render(f"Rolled: {self.last_roll}", True, BLACK)
            screen.blit(result_text, (WIDTH-170, 20))
        small_font = pygame.font.SysFont(None, 24)
        y_offset = 70
        for player in self.players:
            resources = ", ".join(f"{k}:{v}" for k, v in player.resources.items())
            text = small_font.render(f"{player.name}: {resources}", True, BLACK)
            screen.blit(text, (20, y_offset))
            y_offset += 30

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            screen.fill(WHITE)
            self.draw_tiles()
            self.draw_roads()
            self.draw_ui()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.building_road = not self.building_road
                        print("Building Road Mode: ", self.building_road)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = pygame.mouse.get_pos()
                        if WIDTH-150 <= x <= WIDTH-30 and HEIGHT-100 <= y <= HEIGHT-50:
                            self.roll_dice()
                        elif self.building_road:
                            self.place_road((x, y))
                        else:
                            self.place_settlement((x, y))
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.add_player("Alice")
    game.add_player("Bob", is_ai=True)
    game.run()