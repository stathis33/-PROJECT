import pytest
from main import Game, Player

def test_place_settlement_adds_to_player():
    game = Game()
    player = Player("Tester", (255, 0, 0))
    game.players = [player]
    game.current_player_index = 0

    tile = game.tiles[0]
    pos = tile.vertices[0]

    assert len(player.settlements) == 0

    game.place_settlement(pos)

    assert len(player.settlements) == 1
    assert any(game.is_close(s.location, pos) for s in player.settlements)
