import random
import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 750
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

RESOURCE_COLORS = {
        'wood': (0, 153, 100),       # καφέ
        'brick': (255, 148, 40),      # κόκκινο
        'wheat': (236, 216, 136),    # κίτρινο-σταριού
        'sheep': (134, 205, 86),    # πράσινο-απαλό
        'ore': (152, 152, 152),      # γκρι
        
}

# Hexagon settings
TILE_RADIUS = 40

class Player:
    def __init__(self, name, color, is_ai=False):
        self.knights = 0
        self.has_largest_army = False
        self.name = name
        self.color = color
        self.is_ai = is_ai
        self.resources = {'wood': 0, 'brick': 0, 'wheat': 0, 'sheep': 0, 'ore': 0}
        self.settlements = []
        self.roads = []
        self.points = 0
        self.cards = 0
        self.card_points = 0
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
        self.upgraded = False  # False = σπίτι, True = ξενοδοχείο

class Road:
    def __init__(self, owner, start_pos, end_pos):
        self.owner = owner
        self.start_pos = start_pos
        self.end_pos = end_pos

class Harbor:
    def __init__(self, resource_type, ratio, position, edge_vertices):
        self.resource_type = resource_type  # 'wood', 'brick', etc. or None for generic
        self.ratio = ratio  # 2 or 3
        self.position = position  # center for drawing
        self.edge_vertices = edge_vertices  # two vertex positions

class Game:
    def __init__(self):
        dice_sheet = pygame.image.load("dice.png")
        self.dice_faces = []
        self.dice1_face = None
        self.dice2_face = None
        face_width = dice_sheet.get_width() // 3
        face_height = dice_sheet.get_height() // 2
        for row in range(2):
            for col in range(3):
                rect = pygame.Rect(col * face_width, row * face_height, face_width, face_height)
                face = dice_sheet.subsurface(rect)
                face = pygame.transform.scale(face, (64, 64))  # Προσαρμογή μεγέθους
                self.dice_faces.append(face)
        self.current_dice_face = None
        self.longest_road_owner = None
        self.upgrading_settlement = False
        self.message = ""
        self.wheat_harbor_vertex_ids = {26, 27}
        self.ore_harbor_vertex_ids = {39, 49}
        self.sheep_harbor_vertex_ids = {52, 46}
        self.brick_harbor_vertex_ids = {22, 23}
        self.wood_harbor_vertex_ids = {0, 9}
        self.generic_harbor_vertex_ids = {3, 4, 13, 10, 36, 37, 50, 51}
        self.vertex_id_map = {}
        self.vertex_list = []
        self.next_vertex_id = 0
        self.show_bank_menu = False
        self.selected_trade_resource = None
        self.trading_with_bank = False
        self.trade_give = None
        self.trade_receive = None
        self.harbors = []
        self.harbor_images = {
    	    'wood': pygame.image.load('wood.png'),
            'brick': pygame.image.load('brick.png'),
            'wheat': pygame.image.load('wheat.png'),
            'sheep': pygame.image.load('sheep.png'),
            'ore': pygame.image.load('ore.png'),
            '3:1': pygame.image.load('three_to_one.png')  # generic harbor
        }

        original_bg = pygame.image.load("backgr.png")
        self.background = pygame.transform.scale(original_bg, (int(original_bg.get_width() * 1.02), int(original_bg.get_height() * 1.02)))
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
        for key in self.harbor_images:
            self.harbor_images[key] = pygame.transform.scale(self.harbor_images[key], (32, 32))
        
       
    
        

    def draw_screen(self):
        screen.blit(self.background, (-11, -28))
        self.draw_tiles()
        self.draw_roads()
        self.draw_tiles()
        self.draw_roads()
        self.draw_harbors()
        self.draw_ui()
        self.draw_highlights()
        pygame.display.flip()


    def roll_dice(self):
        player = self.players[self.current_player_index]
        if player.has_rolled:
            print("Έχεις ήδη ρίξει τα ζάρια αυτόν τον γύρο!")
            return

        # Animation
        for _ in range(10):
            self.dice1_face = random.choice(self.dice_faces)
            self.dice2_face = random.choice(self.dice_faces)
            self.draw_screen()
            pygame.time.wait(100)

        # Πραγματική ζαριά
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        self.last_roll = die1 + die2
        self.dice1_face = self.dice_faces[die1 - 1]
        self.dice2_face = self.dice_faces[die2 - 1]


        player.has_rolled = True
        print(f"Dice rolled: {self.last_roll}")
        self.distribute_resources()

        
    def show_popup_message(self, text, color=RED):
        font = pygame.font.SysFont(None, 36)
        msg_surface = font.render(text, True, color)
        bg_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 40, 600, 80)
        pygame.draw.rect(screen, (255, 255, 220), bg_rect)  # υπόβαθρο
        pygame.draw.rect(screen, BLACK, bg_rect, 2)         # περίγραμμα
        screen.blit(msg_surface, msg_surface.get_rect(center=bg_rect.center))
        pygame.display.flip()
        pygame.time.wait(1500)


    def get_vertex_id(self, pos):
        for vertex, vid in self.vertex_id_map.items():
            if self.is_close(vertex, pos, threshold=1):
                return vid
        return None

    def assign_vertex_ids(self):
        for tile in self.tiles:
            for vertex in tile.vertices:
                exists = False
                for existing in self.vertex_list:
                    if self.is_close(existing, vertex, threshold=1):
                        exists = True
                        break
                if not exists:
                    self.vertex_list.append(vertex)
                    self.vertex_id_map[vertex] = self.next_vertex_id
                    self.next_vertex_id += 1

    def update_points(self):
        # Πρώτα υπολογίζουμε τον νέο κάτοχο
        new_owner = self.get_longest_road_owner()

        # Αν άλλαξε ο κάτοχος, αφαιρούμε από τον παλιό και προσθέτουμε στον νέο
        if new_owner != self.longest_road_owner:
            if self.longest_road_owner:
                self.longest_road_owner.points -= 2
            if new_owner:
                new_owner.points += 2
            self.longest_road_owner = new_owner

        # Ενημέρωση πόντων από σπίτια / ξενοδοχεία
        for player in self.players:
            base_points = 0
            for settlement in player.settlements:
                if hasattr(settlement, 'upgraded') and settlement.upgraded:
                    base_points += 2
                else:
                    base_points += 1
            # Μην αγγίζεις τους +2 πόντους από δρόμο εδώ, τους χειριζόμαστε ξεχωριστά
            # Συνεπώς, ενημερώνουμε μόνο το base score
            # (δηλ. χωρίς longest road)
            player.base_points = base_points  # optional debug αν θες
            player.points = base_points + player.card_points
            if player == self.longest_road_owner:
                player.points += 2

            if player.has_largest_army:
                player.points += 2

    def check_largest_army(self):
        max_knights = 0
        leader = None

        for p in self.players:
            if p.knights > max_knights:
                max_knights = p.knights
                leader = p
            elif p.knights == max_knights:
                leader = None  # ισοπαλία => κανείς δεν παίρνει τον τίτλο

        for p in self.players:
            if p.has_largest_army and p != leader:
                p.has_largest_army = False
                p.points -= 2
                print(f"{p.name} έχασε τον τίτλο 'Μεγαλύτερος Στρατός'")

        if leader and max_knights >= 3 and not leader.has_largest_army:
            leader.has_largest_army = True
            leader.points += 2
            print(f"{leader.name} πήρε τον τίτλο 'Μεγαλύτερος Στρατός' (+2 πόντοι)")



    def buy_card(self):
        player = self.players[self.current_player_index]
        if (player.resources['sheep'] >= 1 and
            player.resources['wheat'] >= 1 and
            player.resources['ore'] >= 1):
        
            # Αφαίρεση πόρων
            player.resources['sheep'] -= 1
            player.resources['wheat'] -= 1
            player.resources['ore'] -= 1

            # Επιλογή τύπου κάρτας (πόντος ή στρατός)
            card_type = random.choice(['victory_point', 'knight'])
            if card_type == 'victory_point':
                player.card_points += 1
                self.show_popup_message(f"{player.name} πήρε κάρτα! +1 πόντος", color=BLUE)
            else:
                player.knights += 1
                self.show_popup_message(f"{player.name} πήρε κάρτα Στρατού!", color=BLUE)
                self.check_largest_army()

                self.update_points()
        else:
            self.show_popup_message("Δεν έχεις αρκετούς πόρους για κάρτα!", color=RED)



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


    def upgrade_settlement(self, pos):
        player = self.players[self.current_player_index]
        found = False

        for tile in self.tiles:
            for settlement in tile.settlements:
                if self.is_close(settlement.location, pos, threshold=10):
                    found = True
                    if settlement.owner != player:
                        self.show_popup_message("Δεν σου ανήκει αυτό το σπίτι!")
                        return
                    if settlement.upgraded:
                        self.show_popup_message("Έχει ήδη αναβαθμιστεί σε ξενοδοχείο!")
                        return
                    if player.resources['wheat'] < 2 or player.resources['ore'] < 3:
                        self.show_popup_message("Δεν έχεις αρκετούς πόρους!")
                        return

                    # Αναβάθμιση
                    player.resources['wheat'] -= 2
                    player.resources['ore'] -= 3
                    settlement.upgraded = True
                    player.points += 1  # αν θες, δώσε 1 πόντο
                    print(f"{player.name} αναβάθμισε οικισμό σε ξενοδοχείο!")
                    return

        if not found:
            self.show_popup_message("Δεν υπάρχει κοντινός οικισμός για αναβάθμιση.")

  
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
    

    def execute_bank_trade(self):
        player = self.players[self.current_player_index]
        give = self.trade_give
        receive = self.trade_receive

        has_2to1_harbor = False
        has_3to1_harbor = False

        for settlement in player.settlements:
            vertex_id = self.get_vertex_id(settlement.location)
            for harbor in self.harbors:
                if harbor.ratio == 2 and harbor.resource_type == give:
                    if any(self.is_close(settlement.location, vertex, threshold=15) for vertex in harbor.edge_vertices):
                        has_2to1_harbor = True
            
            if give == 'wheat' and vertex_id in self.wheat_harbor_vertex_ids:
                has_2to1_harbor = True

            if give == 'ore' and vertex_id in self.ore_harbor_vertex_ids:
                has_2to1_harbor = True
           
            # Ειδική περίπτωση: settlement σε κορυφή για wood
            if give == 'wood' and vertex_id in self.wood_harbor_vertex_ids:
                has_2to1_harbor = True

            # Ειδική περίπτωση: settlement σε κορυφή για brick
            if give == 'brick' and vertex_id in self.brick_harbor_vertex_ids:
                has_2to1_harbor = True

            # Ειδική περίπτωση: settlement σε κορυφή για sheep
            if give == 'sheep' and vertex_id in self.sheep_harbor_vertex_ids:
                has_2to1_harbor = True

            # Έλεγχος για generic 3:1
            if vertex_id in self.generic_harbor_vertex_ids:
                has_3to1_harbor = True


            

            
           
           

            vertex_id = self.get_vertex_id(settlement.location)
            if vertex_id in self.generic_harbor_vertex_ids:
                has_3to1_harbor = True
            # Ειδική περίπτωση: αν έχει settlement σε κορυφή 0 ή 9, έχει 2:1 για wood
            vertex_id = self.get_vertex_id(settlement.location)
            if give == 'wood' and vertex_id in self.wood_harbor_vertex_ids:
                has_2to1_harbor = True

        if has_2to1_harbor and player.resources[give] >= 2:
            player.resources[give] -= 2
            player.resources[receive] += 1
            print(f"{player.name} exchanged 2 {give} for 1 {receive} (2:1 harbor).")
        elif has_3to1_harbor and player.resources[give] >= 3:
            player.resources[give] -= 3
            player.resources[receive] += 1
            print(f"{player.name} exchanged 3 {give} for 1 {receive} (3:1 harbor).")
        elif player.resources[give] >= 4:
            player.resources[give] -= 4
            player.resources[receive] += 1
            print(f"{player.name} exchanged 4 {give} for 1 {receive} (bank 4:1 trade).")
        else:
            self.show_popup_message("Δεν πληροίς τις προϋποθέσεις για την ανταλλαγή")



    
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
                    if self.trading_with_bank:
                        resources = ['wood', 'brick', 'wheat', 'sheep', 'ore']
                        small_font = pygame.font.SysFont(None, 24)

                        # Επιλογή υλικού προς ΔΩΣΗ
                        for i, res in enumerate(resources):
                            give_rect = pygame.Rect(WIDTH - 140, HEIGHT - 600 + i * 30, 60, 25)
                            if give_rect.collidepoint(x, y):
                                self.trade_give = res
                                print("Δίνεις:", res)

                        # Επιλογή υλικού προς ΛΗΨΗ
                        for i, res in enumerate(resources):
                            receive_rect = pygame.Rect(WIDTH - 140, HEIGHT - 470  + i * 30, 60, 25)
                            if receive_rect.collidepoint(x, y):
                                self.trade_receive = res
                                print("Θέλεις:", res)

                        # Αν έχουν επιλεγεί και τα δύο, κάνε την ανταλλαγή
                        if self.trade_give and self.trade_receive:
                            self.execute_bank_trade()
                            self.trading_with_bank = False
                            self.trade_give = None
                            self.trade_receive = None

                        if self.trade_give and self.trade_receive:
                            self.execute_bank_trade()
                            self.trading_with_bank = False
                            self.trade_give = None
                            self.trade_receive = None

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
        self.setup_harbors()
        self.assign_vertex_ids()
        

    def setup_harbors(self):
        self.harbors = []
        dx = 300
        dy = -25

        # (τύπος, αναλογία, εξωτερική θέση, ακμή εξάγωνου - 2 σημεία)
        harbor_data = [
            ('3:1', 3, (160 + dx, 40), [(180 + dx, 75), (140 + dx, 75)]),       # Πάνω αριστερά
            ('wood', 2, (290 + dx, 40 + dy), [(270 + dx, 75), (310 + dx, 75)]),      # Πάνω
            ('3:1', 3, (420 + dx, 40), [(400 + dx, 75), (440 + dx, 75)]),       # Πάνω δεξιά
            ('brick', 2, (520 + dx, 140), [(500 + dx, 160), (530 + dx, 180)]),  # Δεξιά πάνω
            ('3:1', 3, (520 + dx, 260), [(500 + dx, 260), (530 + dx, 280)]),    # Δεξιά κάτω
            ('sheep', 2, (420 + dx, 370 + 35), [(400 + dx, 335 + 35), (440 + dx, 335)]),  # Κάτω δεξιά
            ('3:1', 3, (290 + dx, 460 + dy), [(270 + dx, 425), (310 + dx, 425)]),    # Κάτω
            ('ore', 2, (160 + dx, 370), [(140 + dx, 335), (180 + dx, 335)]),    # Κάτω αριστερά
            ('wheat', 2, (80 + dx, 260), [(100 + dx, 260), (70 + dx, 280)])     # Αριστερά
        ]

        for res_type, ratio, pos, edge in harbor_data:
            self.harbors.append(Harbor(res_type, ratio, pos, edge))

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
                            self.update_points()
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
                            self.update_points()
                            return

        pygame.time.wait(1000)
        self.end_turn()
        self.update_points()

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

    

    def distribute_resources(self):
        for player in self.players:
            for settlement in player.settlements:
                for tile in self.tiles:
                    if tile.number == self.last_roll:
                        for vertex in tile.vertices:
                            if math.hypot(settlement.location[0] - vertex[0], settlement.location[1] - vertex[1]) < 10:
                                amount = 2 if settlement.upgraded else 1
                                player.resources[tile.resource_type] += amount
                                print(f"{player.name} receives {amount} {tile.resource_type}")
                                break

    def end_turn(self):
        self.update_points()
        self.players[self.current_player_index].has_rolled = False
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print(f"Next player: {self.players[self.current_player_index].name}")
        self.update_points()
        # Έλεγχος για νίκη
        for player in self.players:
            if player.points >= 10:
                self.show_popup_message(f"Ο παίκτης {player.name} είναι ο ΝΙΚΗΤΗΣ!", color=GREEN)
                
                
                

    def draw_ui(self):
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
        player = self.players[self.current_player_index]
        resources = ['wood', 'brick', 'wheat', 'sheep', 'ore']

        # Κουμπί Τράπεζας
        bank_btn = pygame.Rect(WIDTH - 150, HEIGHT - 280, 120, 40)
        pygame.draw.rect(screen, (255, 230, 100), bank_btn)
        bank_text = font.render("Τράπεζα", True, BLACK)
        screen.blit(bank_text, bank_btn.move(10, 8))

        # Αν είναι ενεργή η συναλλαγή, δείξε κουμπιά για Δώσε / Πάρε
        if self.trading_with_bank:
            y_base = HEIGHT - 700
            screen.blit(small_font.render("Δώσε:", True, BLACK), (WIDTH - 140, y_base))
            for i, res in enumerate(resources):
                rect = pygame.Rect(WIDTH - 140, y_base + 30 + i * 30, 60, 25)
                pygame.draw.rect(screen, (200, 200, 255), rect)
                screen.blit(small_font.render(res, True, BLACK), rect.move(5, 5))
                if self.trade_give == res:
                    pygame.draw.rect(screen, RED, rect, 2)

            y_base += 190
            screen.blit(small_font.render("Πάρε:", True, BLACK), (WIDTH - 140, y_base))
            for i, res in enumerate(resources):
                rect = pygame.Rect(WIDTH - 140, y_base + 30 + i * 30, 60, 25)
                pygame.draw.rect(screen, (200, 255, 200), rect)
                screen.blit(small_font.render(res, True, BLACK), rect.move(5, 5))
                if self.trade_receive == res:
                    pygame.draw.rect(screen, GREEN, rect, 2)

        # Κουμπί Roll Dice
        roll_btn_color = (180, 180, 180) if player.has_rolled else YELLOW
        roll_text_color = (100, 100, 100) if player.has_rolled else BLACK
        roll_text = font.render("Roll Dice", True, roll_text_color)
        pygame.draw.rect(screen, roll_btn_color, (WIDTH - 150, HEIGHT - 100, 120, 40))
        screen.blit(roll_text, (WIDTH - 145, HEIGHT - 90))

        # Κουμπί Τέλος
        end_turn_text = font.render("Τέλος", True, BLACK)
        pygame.draw.rect(screen, (200, 200, 200), (WIDTH - 150, HEIGHT - 160, 120, 40))
        screen.blit(end_turn_text, (WIDTH - 145, HEIGHT - 150))
        
        # Κουμπί Πάρε Κάρτα
        card_btn = pygame.Rect(WIDTH - 300, HEIGHT - 100, 120, 40)
        pygame.draw.rect(screen, (200, 180, 255), card_btn)
        card_text = font.render("Κάρτα", True, BLACK)
        screen.blit(card_text, card_btn.move(5, 8))


      
        # Κουμπί Δρόμος / Οικισμός
        build_mode_text = font.render(("Δρόμος" if self.building_road else "Οικισμός"), True, BLACK)
        pygame.draw.rect(screen, (240, 83, 85), (WIDTH - 150, HEIGHT - 220, 120, 40))
        screen.blit(build_mode_text, (WIDTH - 145, HEIGHT - 210))
        
        # Κουμπί Αναβάθμιση
        upgrade_text = font.render("πολ/κία", True, BLACK)
        pygame.draw.rect(screen, (255, 180, 130), (WIDTH - 150, HEIGHT - 340, 120, 40))
        screen.blit(upgrade_text, (WIDTH - 145, HEIGHT - 330))


        

 
        # Εμφάνιση αποτελέσματος ζαριών
        if self.dice1_face and self.dice2_face:
            screen.blit(self.dice1_face, (WIDTH - 160, 20))
            screen.blit(self.dice2_face, (WIDTH - 90, 20))



        # Τρέχων παίκτης
        turn_text = font.render(f"Παίζει ο: {player.name}", True, player.color)
        screen.blit(turn_text, (20, 20))


        for tile in self.tiles:
            for settlement in tile.settlements:
        
                if settlement.upgraded:
                    pygame.draw.circle(screen, settlement.owner.color, settlement.location, 12)
                    pygame.draw.circle(screen, BLACK, settlement.location, 12, 2)
                else:
                    pygame.draw.circle(screen, settlement.owner.color, settlement.location, 8)

                
        # Πόροι παικτών
        y_offset = HEIGHT - 200
        for p in self.players:
       	    name_text = small_font.render(f"{p.name} ({p.points})", True, p.color)
       	    screen.blit(name_text, (20, y_offset))
            knight_text = small_font.render(f"Στρατός: {p.knights}", True, BLACK)
            screen.blit(knight_text, (20, y_offset + 18))
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
            fill_color = RESOURCE_COLORS.get(tile.resource_type, WHITE)
            self.draw_hexagon(screen, BLACK, tile.position, TILE_RADIUS, fill_color=fill_color)
            font = pygame.font.SysFont(None, 24)
            number_text = font.render(str(tile.number), True, BLUE)
            screen.blit(number_text, number_text.get_rect(center=tile.position))

            resource_img = self.resource_images.get(tile.resource_type)
            if resource_img:
                img_rect = resource_img.get_rect(center=(tile.position[0], tile.position[1] + 25))
                screen.blit(resource_img, img_rect)

            # ✅ Εδώ είναι το σωστό σημείο
            for settlement in tile.settlements:
                if hasattr(settlement, 'upgraded') and settlement.upgraded:
                    pygame.draw.circle(screen, settlement.owner.color, settlement.location, 12)
                    pygame.draw.circle(screen, BLACK, settlement.location, 12, 2)
                else:
                    pygame.draw.circle(screen, settlement.owner.color, settlement.location, 8)

    def draw_harbors(self):
        font = pygame.font.SysFont(None, 16)
        for harbor in self.harbors:
            # Εικόνα λιμανιού
            img = self.harbor_images.get(harbor.resource_type)
            if img:
                img_rect = img.get_rect(center=harbor.position)
                screen.blit(img, img_rect)

            # Ετικέτα 
            label = f"{harbor.ratio}:1" if harbor.resource_type == '3:1' else f"{harbor.resource_type} 2:1"
            text = font.render(label, True, BLACK)
            screen.blit(text, (harbor.position[0] - 20, harbor.position[1] + 18))

    def trade_with_bank(self, give_type, get_type):
        player = self.players[self.current_player_index]
    
        # Έλεγχος αν έχει ο παίκτης οικισμό σε λιμάνι 2:1 αυτού του τύπου
        has_matching_harbor = False
        for harbor in self.harbors:
            if harbor.ratio == 2 and harbor.resource_type == give_type:
                for settlement in player.settlements:
                    if any(self.is_close(settlement.location, vertex, threshold=10) for vertex in harbor.edge_vertices):
                        has_matching_harbor = True
                        break
    
        if has_matching_harbor:
            if player.resources[give_type] >= 2:
                player.resources[give_type] -= 2
                player.resources[get_type] += 1
                print(f"{player.name} exchanged 2 {give_type} for 1 {get_type}")
            else:
                print("Δεν έχεις αρκετούς πόρους για να κάνεις συναλλαγή.")
        else:
            print("Δεν έχεις πρόσβαση σε λιμάνι για αυτό το είδος.")

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

    def draw_hexagon(self, surface, color, position, radius, fill_color=None):
        x, y = position
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            point_x = x + radius * math.cos(angle_rad)
            point_y = y + radius * math.sin(angle_rad)
            points.append((point_x, point_y))
        if fill_color:
            pygame.draw.polygon(surface, fill_color, points)
        pygame.draw.polygon(surface, color, points, 2)

    def handle_trade(self, give_resource):
        player = self.players[self.current_player_index]
    
        # Έλεγξε αν έχει settlement σε λιμάνι 2:1 για το συγκεκριμένο υλικό
        eligible = False
        for harbor in self.harbors:
            if harbor.resource_type == give_resource and harbor.ratio == 2:
                for settlement in player.settlements:
                    if self.is_close(settlement.location, harbor.edge_vertices[0], 20) or \
                        self.is_close(settlement.location, harbor.edge_vertices[1], 20):
                        eligible = True
                        break
        if not eligible:
            print("Δεν έχεις πρόσβαση στο λιμάνι 2:1 για αυτό το υλικό.")
            return

        # Έλεγξε αν έχει 2 υλικά να δώσει
        if player.resources[give_resource] < 2:
            print(f"Δεν έχεις 2 {give_resource} για ανταλλαγή.")
            return

        # Κάνε ανταλλαγή
        player.resources[give_resource] -= 2
        wanted_resource = random.choice(['wood', 'brick', 'wheat', 'sheep', 'ore'])
        player.resources[wanted_resource] += 1
        print(f"Έδωσες 2 {give_resource} και πήρες 1 {wanted_resource}")

    def run(self):
        self.show_start_screen()
        self.setup_players()
        clock = pygame.time.Clock()
        running = True
        while running:
            screen.blit(self.background, (-11, -28))
            self.draw_tiles()
            self.draw_roads()
            self.draw_tiles()
            self.draw_roads()
            self.draw_harbors()  
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
                    resources = ['wood', 'brick', 'wheat', 'sheep', 'ore']
                    # Επιλογή για Δώσε
                    for i, res in enumerate(resources):
                        give_rect = pygame.Rect(WIDTH - 140, HEIGHT - 665 + i * 30, 60, 25)
                        if give_rect.collidepoint(x, y):
                            self.trade_give = res
                            print("Δίνεις:", res)
                           

                    # Επιλογή για Πάρε
                    for i, res in enumerate(resources):
                        receive_rect = pygame.Rect(WIDTH - 140, HEIGHT - 470 + i * 30, 60, 25)
                        if receive_rect.collidepoint(x, y):
                            self.trade_receive = res
                            print("Θέλεις:", res)
                            
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Δεξί κλικ
                         self.upgrade_settlement(pygame.mouse.get_pos())

                    # Αν έχουν επιλεγεί και τα δύο, κάνε την ανταλλαγή
                    if self.trade_give and self.trade_receive:
                        self.execute_bank_trade()
                        self.trading_with_bank = False
                        self.trade_give = None
                        self.trade_receive = None
                       

                    if WIDTH - 150 <= x <= WIDTH - 30 and HEIGHT - 100 <= y <= HEIGHT - 60:
                        self.roll_dice()
                    if self.trading_with_bank:
                        resources = ['wood', 'brick', 'wheat', 'sheep', 'ore']

                        # Δώσε
                        for i, res in enumerate(resources):
                            give_rect = pygame.Rect(WIDTH - 140, HEIGHT - 665 + i * 30, 60, 25)
                            if give_rect.collidepoint(x, y):
                                self.trade_give = res
                                

                        # Πάρε
                        for i, res in enumerate(resources):
                            receive_rect = pygame.Rect(WIDTH - 140, HEIGHT - 470 + i * 30, 60, 25)
                            if receive_rect.collidepoint(x, y):
                                self.trade_receive = res
                                

                        # Αν και τα δύο έχουν οριστεί, κάνε την ανταλλαγή
                        if self.trade_give and self.trade_receive:
                            self.execute_bank_trade()
                            self.trading_with_bank = False
                            self.trade_give = None
                            self.trade_receive = None
                            

                    if self.show_bank_menu:
                        resources = ['wood', 'brick', 'wheat', 'sheep', 'ore']
                        for i, res in enumerate(resources):
                            btn_rect = pygame.Rect(WIDTH - 150, HEIGHT - 330 - i * 45, 120, 40)
                            if btn_rect.collidepoint(x, y):
                                self.handle_trade(res)
                   

                    elif WIDTH - 150 <= x <= WIDTH - 30 and HEIGHT - 160 <= y <= HEIGHT - 120:
                        self.end_turn()
                        self.update_points()
                    elif WIDTH - 150 <= x <= WIDTH - 30 and HEIGHT - 220 <= y <= HEIGHT - 180:
                        self.building_road = not self.building_road
                        print("Building mode:", "Road" if self.building_road else "Settlement")
                    elif self.building_road:
                        self.place_road((x, y))
                    elif WIDTH - 300 <= x <= WIDTH - 200 and HEIGHT - 110 <= y <= HEIGHT - 50:
                        self.buy_card()
                    elif WIDTH - 150 <= x <= WIDTH - 30 and HEIGHT - 280 <= y <= HEIGHT - 240:
                        self.trading_with_bank = not self.trading_with_bank
                        self.trade_give = None
                        self.trade_receive = None
                    elif WIDTH - 150 <= x <= WIDTH - 30 and HEIGHT - 340 <= y <= HEIGHT - 300:
                        self.upgrading_settlement = True
                        print("Κάνε κλικ σε οικισμό για αναβάθμιση")

                    else:
                        if self.upgrading_settlement:
                            self.upgrade_settlement((x, y))
                            self.upgrading_settlement = False
                        else:
                            self.place_settlement((x, y))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
