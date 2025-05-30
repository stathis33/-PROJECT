import pytest
from main import Game, Player

def test_roll_dice_range():
    game = Game()
    player = Player("Tester", (255, 0, 0))
    game.players = [player]
    game.current_player_index = 0

    game.roll_dice()

    assert 2 <= game.last_roll <= 12, f"Invalid dice roll: {game.last_roll}"
