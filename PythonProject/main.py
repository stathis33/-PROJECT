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
        self.has_rolled = False
        self.initial_settlements_placed = 0

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
        self.resource_images = {
            'wood': pygame.image.load('wood.png'),
            'wheat': pygame.image.load('wheat.png'),
            'ore': pygame.image.load('ore.png'),
            'brick': pygame.image.load('brick.png'),
            'sheep': pygame.image.load('sheep.png')
        }
        for key in self.resource_images:
            self.resource_images[key] = pygame.transform.scale(self.resource_images[key], (32, 32))

    def show_start_screen(self):
        waiting = True
        font = pygame.font.SysFont(None, 60)
        play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 60)
        clock = pygame.time.Clock()

        while waiting:
            screen.fill(WHITE)
            pygame.draw.rect(screen, (100, 200, 100), play_button)
            play_text = font.render("Play", True, BLACK)
            screen.blit(play_text, play_text.get_rect(center=play_button.center))
            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.collidepoint(pygame.mouse.get_pos()):
                        waiting = False

    def setup_players(self):
        choosing = True
        font = pygame.font.SysFont(None, 40)
        clock = pygame.time.Clock()
        options = [2, 3, 4]
        selected_players = None

        while choosing:
            screen.fill(WHITE)
            title = font.render("Πόσοι παίκτες;", True, BLACK)
            screen.blit(title, (WIDTH // 2 - 100, 100))

            buttons = []
            for i, opt in enumerate(options):
                rect = pygame.Rect(WIDTH // 2 - 50, 180 + i * 70, 100, 50)
                pygame.draw.rect(screen, (100, 200, 100), rect)
                text = font.render(str(opt), True, BLACK)
                screen.blit(text, text.get_rect(center=rect.center))
                buttons.append((rect, opt))

            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, val in buttons:
                        if rect.collidepoint(event.pos):
                            selected_players = val
                            choosing = False

        for i in range(selected_players):
            choosing_ai = True
            while choosing_ai:
                screen.fill(WHITE)
                question = font.render(f"Παίκτης {i+1} είναι AI;", True, BLACK)
                screen.blit(question, (WIDTH // 2 - 130, 100))

                yes_btn = pygame.Rect(WIDTH // 2 - 100, 180, 80, 50)
                no_btn = pygame.Rect(WIDTH // 2 + 20, 180, 80, 50)

                pygame.draw.rect(screen, (0, 200, 0), yes_btn)
                pygame.draw.rect(screen, (200, 0, 0), no_btn)

                screen.blit(font.render("Ναι", True, BLACK), yes_btn.move(10, 10))
                screen.blit(font.render("Όχι", True, BLACK), no_btn.move(10, 10))
                pygame.display.flip()
                clock.tick(60)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if yes_btn.collidepoint(event.pos):
                            self.add_player(f"Παίκτης {i+1}", is_ai=True)
                            choosing_ai = False
                        elif no_btn.collidepoint(event.pos):
                            self.add_player(f"Παίκτης {i+1}", is_ai=False)
                            choosing_ai = False
    def setup_tiles(self):
        resources = ['wood', 'wheat', 'ore', 'brick', 'sheep', 'wheat', 'brick', 'ore', 'wheat',
                     'brick', 'wheat', 'wood', 'sheep', 'wood', 'wood', 'sheep', 'sheep', 'ore', 'brick']
        numbers = [5, 3, 2, 12, 5, 6, 4, 8, 4, 11, 7, 9, 8, 9, 12, 10, 11, 10, 6]
        x_offset = TILE_RADIUS * math.sqrt(3)
        y_offset = TILE_RADIUS * 1.5
        rows = [3, 4, 5, 4, 3, 1]
        start_y = 100
        idx = 0
        for row_idx, tiles_in_row in enumerate(rows):
            start_x = WIDTH / 2 - (tiles_in_row - 1) * x_offset / 2
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

    def is_close(self, pos1, pos2, threshold=10):
        return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1]) < threshold

    def play_ai_turn(self):
        player = self.players[self.current_player_index]
        if not player.is_ai:
            return

        print(f"AI turn: {player.name}")

        if player.initial_settlements_placed < 2:
            for tile in self.tiles:
                for vertex in tile.vertices:
                    too_close = False
                    for other_tile in self.tiles:
                        for settlement in other_tile.settlements:
                            if self.is_close(vertex, settlement.location, threshold=55):
                                too_close = True
                    if not too_close:
                        self.place_settlement(vertex)
                        player.initial_settlements_placed += 1

                        for i in range(6):
                            start = tile.vertices[i]
                            end = tile.vertices[(i + 1) % 6]
                            mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
                            if self.is_close(vertex, start) or self.is_close(vertex, end):
                                self.place_road(mid)
                                break

                        pygame.time.wait(800)
                        if player.initial_settlements_placed < 2:
                            self.end_turn()
                        return

        if not player.has_rolled:
            self.roll_dice()

        for settlement in player.settlements:
            for tile in self.tiles:
                vertices = tile.vertices
                for i in range(6):
                    start = vertices[i]
                    end = vertices[(i + 1) % 6]
                    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)

                    if self.is_close(settlement.location, start) or self.is_close(settlement.location, end):
                        exists = any(
                            (road.start_pos == start and road.end_pos == end) or
                            (road.start_pos == end and road.end_pos == start)
                            for road in self.roads
                        )
                        if not exists:
                            self.place_road(mid)
                            pygame.time.wait(1000)
                            self.end_turn()
                            return

        pygame.time.wait(1000)
        self.end_turn()

    def place_settlement(self, pos):
        for tile in self.tiles:
            for vertex in tile.vertices:
                dist = math.hypot(pos[0] - vertex[0], pos[1] - vertex[1])
                if dist < 10:
                    for other_tile in self.tiles:
                        for settlement in other_tile.settlements:
                            if self.is_close(vertex, settlement.location, threshold=55):
                                font = pygame.font.SysFont(None, 36)
                                warning = font.render("Απαγορεύεται! Πολύ κοντά σε άλλον οικισμό.", True, RED)
                                screen.blit(warning, (WIDTH // 2 - 200, HEIGHT - 250))
                                pygame.display.flip()
                                pygame.time.wait(1500)
                                return
                    player = self.players[self.current_player_index]
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
                    return

    def place_road(self, pos):
        min_dist = float('inf')
        best_start = None
        best_end = None
        for tile in self.tiles:
            vertices = tile.vertices
            for i in range(6):
                start = vertices[i]
                end = vertices[(i + 1) % 6]
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
                if (road.start_pos == best_start and road.end_pos == best_end) or \
                   (road.start_pos == best_end and road.end_pos == best_start):
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

    def roll_dice(self):
        player = self.players[self.current_player_index]
        if player.has_rolled:
            print("Έχεις ήδη ρίξει τα ζάρια αυτόν τον γύρο!")
            return
        self.last_roll = random.randint(1, 6) + random.randint(1, 6)
        player.has_rolled = True
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

    def end_turn(self):
        self.players[self.current_player_index].has_rolled = False
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print(f"Next player: {self.players[self.current_player_index].name}")
    def draw_ui(self):
        font = pygame.font.SysFont(None, 36)
        player = self.players[self.current_player_index]
        roll_btn_color = (180, 180, 180) if player.has_rolled else YELLOW
        roll_text_color = (100, 100, 100) if player.has_rolled else BLACK
        roll_text = font.render("Roll Dice", True, roll_text_color)
        pygame.draw.rect(screen, roll_btn_color, (WIDTH - 150, HEIGHT - 100, 120, 40))
        screen.blit(roll_text, (WIDTH - 145, HEIGHT - 90))

        end_turn_text = font.render("Τέλος", True, BLACK)
        pygame.draw.rect(screen, (200, 200, 200), (WIDTH - 150, HEIGHT - 160, 120, 40))
        screen.blit(end_turn_text, (WIDTH - 145, HEIGHT - 150))

        build_mode_text = font.render(("Δρόμος" if self.building_road else "Οικισμός"), True, BLACK)
        pygame.draw.rect(screen, (180, 220, 255), (WIDTH - 150, HEIGHT - 220, 120, 40))
        screen.blit(build_mode_text, (WIDTH - 145, HEIGHT - 210))

        if self.last_roll is not None:
            result_text = font.render(f"Rolled: {self.last_roll}", True, BLACK)
            screen.blit(result_text, (WIDTH - 170, 20))

        turn_text = font.render(f"Παίζει ο: {player.name}", True, player.color)
        screen.blit(turn_text, (20, 20))

        small_font = pygame.font.SysFont(None, 24)
        y_offset = HEIGHT - 100
        for p in self.players:
            name_text = small_font.render(p.name, True, p.color)
            screen.blit(name_text, (20, y_offset))

            x_offset = 130
            for res_type, amount in p.resources.items():
                icon = self.resource_images.get(res_type)
                if icon:
                    screen.blit(icon, (x_offset, y_offset))
                    amt_text = small_font.render(str(amount), True, BLACK)
                    screen.blit(amt_text, (x_offset + 35, y_offset + 8))
                    x_offset += 70
            y_offset += 40

    def draw_tiles(self):
        for tile in self.tiles:
            self.draw_hexagon(screen, BLACK, tile.position, TILE_RADIUS)
            font = pygame.font.SysFont(None, 24)
            number_text = font.render(str(tile.number), True, BLUE)
            screen.blit(number_text, number_text.get_rect(center=tile.position))
            resource_img = self.resource_images.get(tile.resource_type)
            if resource_img:
                img_rect = resource_img.get_rect(center=(tile.position[0], tile.position[1] + 25))
                screen.blit(resource_img, img_rect)
            for settlement in tile.settlements:
                pygame.draw.circle(screen, settlement.owner.color, settlement.location, 8)

    def draw_highlights(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.building_road:
            for tile in self.tiles:
                vertices = tile.vertices
                for i in range(6):
                    start = vertices[i]
                    end = vertices[(i + 1) % 6]
                    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
                    dist = math.hypot(mouse_pos[0] - mid[0], mouse_pos[1] - mid[1])
                    if dist < 20:
                        pygame.draw.line(screen, (150, 150, 255), start, end, 3)
        else:
            for tile in self.tiles:
                for vertex in tile.vertices:
                    dist = math.hypot(mouse_pos[0] - vertex[0], mouse_pos[1] - vertex[1])
                    if dist < 15:
                        pygame.draw.circle(screen, (100, 255, 100), vertex, 8, 2)

    def draw_roads(self):
        for road in self.roads:
            pygame.draw.line(screen, road.owner.color, road.start_pos, road.end_pos, 5)

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

    def run(self):
        self.show_start_screen()
        self.setup_players()
        clock = pygame.time.Clock()
        running = True
        while running:
            screen.fill(WHITE)
            self.draw_tiles()
            self.draw_roads()
            self.draw_ui()
            self.draw_highlights()

            if self.players[self.current_player_index].is_ai:
                self.play_ai_turn()
                pygame.display.flip()
                clock.tick(60)
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    if WIDTH - 150 <= x <= WIDTH - 30 and HEIGHT - 100 <= y <= HEIGHT - 60:
                        self.roll_dice()
                    elif WIDTH - 150 <= x <= WIDTH - 30 and HEIGHT - 160 <= y <= HEIGHT - 120:
                        self.end_turn()
                    elif WIDTH - 150 <= x <= WIDTH - 30 and HEIGHT - 220 <= y <= HEIGHT - 180:
                        self.building_road = not self.building_road
                        print("Building mode:", "Road" if self.building_road else "Settlement")
                    elif self.building_road:
                        self.place_road((x, y))
                    else:
                        self.place_settlement((x, y))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
