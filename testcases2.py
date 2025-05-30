from game_logic import Game, Player, Road

def test_longest_road_two_players():
    game = Game()

    player1 = Player("P1", (255, 0, 0))
    player2 = Player("P2", (0, 0, 255))
    game.players = [player1, player2]

    road1 = Road(player1, (0, 0), (1, 0))
    road2 = Road(player1, (1, 0), (2, 0))
    player1.roads = [road1, road2]

    road3 = Road(player2, (10, 0), (11, 0))
    road4 = Road(player2, (11, 0), (12, 0))
    road5 = Road(player2, (12, 0), (13, 0))
    player2.roads = [road3, road4, road5]

    game.roads = player1.roads + player2.roads

    owner = game.get_longest_road_owner()

    assert owner == player2, "Ο παίκτης 2 έπρεπε να κερδίσει με 3 συνεχόμενους δρόμους"
    print("✅ test_longest_road_two_players passed.")

if __name__ == "__main__":
    test_longest_road_two_players()
