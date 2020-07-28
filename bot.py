from typing import Counter, Union, List
from constants import ACTION_PHASE, BUY_PHASE, TREASURE_PHASE
import pandas as pd


def bot_actions(state: 'State'):
    card_names = [card.name for card in state.supply]
    return


def bot_state(player, state: 'State'):
    hand_df = cards_to_vec(player.hand, 'num_', '_in_hand', state)  # TODO: Mapping from counter to vector
    hand_size_df = pd.DataFrame([sum(player.hand.values())], columns=['hand_size'])
    discard_pile_df = cards_to_vec(player.discard_pile, 'num_', '_in_discard', state)
    discard_pile_size_df = pd.DataFrame([len(player.discard_pile)], columns=['discard_pile_size'])
    draw_pile_df = cards_to_vec(player.draw_pile, 'num_', '_in_draw', state)
    draw_pile_size_df = pd.DataFrame([len(player.draw_pile)], columns=['draw_pile_size'])
    num_buys_df = pd.DataFrame([player.buys], columns=['num_buys'])
    num_coins_df = pd.DataFrame([player.money], columns=['num_money'])
    num_actions_df = pd.DataFrame([player.actions], columns=['num_actions'])
    num_vp_df = pd.DataFrame([player.victory_points], columns=['num_vp'])

    is_bot_turn_df = pd.DataFrame([int(state.current_player == player)], columns=['is_bot_turn'])
    played_cards_df = cards_to_vec(player.play_area, 'num_', '_in_play', state)

    latest_played = [] if not player.play_area else [player.play_area[-1]]
    latest_played_df = cards_to_vec(latest_played, 'latest_', '_in_play', state)

    phases = [ACTION_PHASE, TREASURE_PHASE, BUY_PHASE]
    phase_df = pd.DataFrame([[[state.phase].count(phase) for phase in phases]], columns=phases)

    supply_pile_sizes = pd.DataFrame([[card.supply_pile_size for card in state.supply]],
                                     columns=['supply_size_' + card.name for card in state.supply])

    features = [
        hand_df,
        hand_size_df,
        discard_pile_df,
        discard_pile_size_df,
        draw_pile_df,
        draw_pile_size_df,
        num_buys_df,
        num_coins_df,
        num_actions_df,
        is_bot_turn_df,
        played_cards_df,
        latest_played_df,
        phase_df,
        supply_pile_sizes,
        num_vp_df,
    ]
    return pd.concat(features, axis=1)


def cards_to_vec(cards: Union[List, Counter], prefix: str, suffix: str, state: 'State'):
    columns = [card.name for card in state.supply]
    if isinstance(cards, list):
        values = [cards.count(card_name) for card_name in columns]
    else:
        values = [cards[card_name] for card_name in columns]
    return pd.DataFrame([values], columns=[prefix + card_name + suffix for card_name in columns])
