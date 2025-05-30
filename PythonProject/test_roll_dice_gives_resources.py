import pytest
from main import Game, Player, Settlement

def test_roll_dice_gives_resources():
    game = Game()
    player = Player("Tester", (255, 0, 0))
    game.players = [player]
    game.current_player_index = 0

    # Χειροκίνητα ορίζουμε ένα tile με known number (π.χ. 8)
    test_tile = game.tiles[0]
    test_tile.number = 8
    test_tile.resource_type = 'wood'

    # Βάζουμε settlement δίπλα στο tile
    pos = test_tile.vertices[0]
    settlement = Settlement(player, pos)
    test_tile.settlements.append(settlement)
    player.settlements.append(settlement)

    # Δίνουμε roll που ταιριάζει με το tile number
    game.last_roll = 8
    game.distribute_resources()

    # Ελέγχουμε ότι ο παίκτης πήρε 1 wood
    assert player.resources['wood'] >= 1, "Ο παίκτης δεν πήρε τον πόρο!"
