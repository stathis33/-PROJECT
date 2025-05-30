import pytest
from main import Game, Player, Settlement

def test_place_road_adds_road_to_player():
    game = Game()
    player = Player("Tester", (255, 0, 0))
    game.players = [player]
    game.current_player_index = 0

    # Προσθέτουμε settlement χειροκίνητα για να μπορεί να ξεκινήσει ο δρόμος από εκεί
    tile = game.tiles[0]
    start = tile.vertices[0]
    end = tile.vertices[1]
    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)

    settlement = Settlement(player, start)
    tile.settlements.append(settlement)
    player.settlements.append(settlement)

    # Ο παίκτης έχει 2 free roads στην αρχή, οπότε δεν απαιτούνται πόροι
    assert len(player.roads) == 0
    assert len(game.roads) == 0

    game.place_road(mid)

    # Έλεγχοι
    assert len(player.roads) == 1
    assert len(game.roads) == 1

    road = player.roads[0]
    assert game.is_close(road.start_pos, start) or game.is_close(road.end_pos, start)
