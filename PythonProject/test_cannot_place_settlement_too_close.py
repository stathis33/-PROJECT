
import pytest
from main import Game, Player, Settlement

def test_cannot_place_settlement_too_close():
    game = Game()
    player = Player("Tester", (255, 0, 0))
    game.players = [player]
    game.current_player_index = 0

    tile = game.tiles[0]
    pos1 = tile.vertices[0]
    pos2 = tile.vertices[1]  # συνήθως κοντινή κορυφή

    # Τοποθετούμε οικισμό στη pos1
    settlement = Settlement(player, pos1)
    tile.settlements.append(settlement)
    player.settlements.append(settlement)

    # Προσπαθούμε να τοποθετήσουμε δεύτερο πολύ κοντά
    before_count = len(player.settlements)
    game.place_settlement(pos2)
    after_count = len(player.settlements)

    # Αν το παιχνίδι δουλεύει σωστά, δεν θα προστεθεί δεύτερος
    assert after_count == before_count, "Ο παίκτης δεν θα έπρεπε να μπορεί να τοποθετήσει κοντινό οικισμό"
