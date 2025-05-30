import pytest
from main import Game, Player

def test_buy_card_consumes_resources_and_awards_effect():
    game = Game()
    player = Player("Tester", (255, 0, 0))
    game.players = [player]
    game.current_player_index = 0

    # Δίνουμε ακριβώς τους πόρους για αγορά κάρτας
    player.resources = {
        'wood': 0, 'brick': 0,
        'sheep': 1, 'wheat': 1, 'ore': 1
    }

    points_before = player.card_points
    knights_before = player.knights

    game.buy_card()

    # Βεβαιωνόμαστε ότι καταναλώθηκαν οι πόροι
    assert player.resources['sheep'] == 0
    assert player.resources['wheat'] == 0
    assert player.resources['ore'] == 0

    # Ελέγχουμε ότι πήρε είτε πόντο είτε στρατιώτη
    assert player.card_points > points_before or player.knights > knights_before
