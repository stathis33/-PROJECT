from game_logic import Game, Player, Road

def test_longest_road_simple():
    game = Game()

    player = Player("Tester", (255, 0, 0))
    game.players = [player]

    road1 = Road(player, (0, 0), (1, 0))
    road2 = Road(player, (1, 0), (2, 0))
    road3 = Road(player, (2, 0), (3, 0))

    player.roads = [road1, road2, road3]
    game.roads = player.roads.copy()

    owner = game.get_longest_road_owner()

    assert owner == player, "Ο παίκτης δεν αναγνωρίστηκε ως κάτοχος του μεγαλύτερου δρόμου"
    print("✅ test_longest_road_simple passed.")

if __name__ == "__main__":
    test_longest_road_simple()
