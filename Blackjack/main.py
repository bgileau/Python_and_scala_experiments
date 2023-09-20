import random
import sys
import os


# Single Deck, with counts
def create_initial_deck():
    global deck
    # 1 = Ace, 2 = 2, etc..., 10 = 10, 11 = Jack, 12 = Queen, 13 = King
    for i in range(1, 14):
        deck[i] = 4


def get_card_value(random_value, who_draw):
    # Grab the value of the card, but be flexible enough to change Ace value should it need to be changed.
    global player_hand
    global dealer_hand
    card_value = 0

    if random_value >= 2 and random_value <= 10:
        card_value = random_value
    elif random_value >= 11:
        card_value = 10 # Jack, Queen, King (11, 12, 13) go to 10.
    elif random_value == 1:
        # Handle ace
        hand_val = get_hand_value(who_draw)
        # If the ace will make the person bust, then assign it a 1. Otherwise, it's an 11.
        if hand_val + 11 > 21:
            modify_hand_value(who_draw)  # Modify the existing ace to be 1 also and make new ace a 1
            card_value = 1
        else:
            card_value = 11

    return card_value


# Hi-Op 1 (good for single deck) counting system
# todo: maybe try out a few card counting systems + dealer + basic strategy?
def get_deck_value_card_counting():
    global player_hand
    global dealer_hand
    global true_count

    global card_methodology

    true_count = 0

    revealed_card_list = [dealer_hand[0]]

    for card in player_hand:
        revealed_card_list.append(card)

    if card_methodology == "Hi-Opt 1":
        for card in revealed_card_list:
            if card >= 3 and card <= 6:  # Check indicies 3-6 and make it +1
                true_count = true_count + 1
            elif card >= 10 and card <= 13:  # Check indicies 10-13 and make it +1
                true_count = true_count - 1

    elif card_methodology == "Hi-Lo 1":
        for card in revealed_card_list:
            if card >= 2 and card <= 6:  # Check indicies 2-6 and make it +1
                true_count = true_count + 1
            elif card >= 10 and card <= 13 or card == 1:  # Check indicies 10-13 (and 1) and make it +1
                true_count = true_count - 1


    print("COUNTING", revealed_card_list, true_count)

    #return true_count


# Illustrious 18 and Fab 4 surrenders
def get_player_action_card_counting():
    global true_count
    global player_hand
    global dealer_hand

    #print(true_count)

    # Check if play is covered in indexing, if not, then revert to basic strategy.

    # First, consider the index. Then, consider the hand to avoid multiple conflicting issues.

    dealer_upcard = dealer_hand[0]
    hand_val = get_hand_value("Player")

    # keys are [hand_val of Player vs upcard of Dealer]

    if hand_val == 16 and dealer_upcard == 10 and true_count >= 0:
        action = "S"
    elif hand_val == 15 and dealer_upcard == 10 and true_count >= 4:
        action = "S"
    elif player_hand[0] == 10 and player_hand[1] == 10 and len(player_hand) == 2 and dealer_upcard == 5 and true_count >= 5:
        action = "P"
    elif player_hand[0] == 10 and player_hand[1] == 10 and len(player_hand) == 2 and dealer_upcard == 6 and true_count >= 5:
        action = "P"
    elif hand_val == 10 and dealer_upcard == 10 and true_count >= 3:
        action = "D"
    elif hand_val == 12 and dealer_upcard == 3 and true_count >= 3:
        action = "S"
    elif hand_val == 12 and dealer_upcard == 2 and true_count >= 4:
        action = "S"
    elif hand_val == 11 and dealer_upcard == 11 and true_count >= -1:
        action = "D"
    elif hand_val == 9 and dealer_upcard == 2 and true_count >= 1:
        action = "D"
    elif hand_val == 10 and dealer_upcard == 11 and true_count >= 2:
        action = "D"
    elif hand_val == 9 and dealer_upcard == 7 and true_count >= 4:
        action = "D"
    elif hand_val == 16 and dealer_upcard == 9 and true_count >= 5:
        action = "D"
    elif hand_val == 13 and dealer_upcard == 2 and true_count <= 0:  # # 14 it switches to "or lower"
        action = "H"
    elif hand_val == 12 and dealer_upcard == 4 and true_count <= 1:
        action = "H"
    elif hand_val == 12 and dealer_upcard == 5 and true_count <= 0:
        action = "H"
    elif hand_val == 12 and dealer_upcard == 6 and true_count <= 1:  # 17
        action = "H"
    elif hand_val == 13 and dealer_upcard == 3 and true_count <= -1:  # 18
        action = "H"
    # Do fab 4 surrenders here
    elif hand_val == 14 and dealer_upcard == 10 and true_count >= 3:
        action = "Sur"
    elif hand_val == 15 and dealer_upcard == 10 and true_count >= 0:
        action = "Sur"
    elif hand_val == 15 and dealer_upcard == 9 and true_count >= 2:
        action = "Sur"
    elif hand_val == 15 and (dealer_upcard == 11 or dealer_upcard == 1) and true_count >= 1:
        action = "Sur"

    else:
        action = get_player_action_basic_strategy()

    return action


def get_player_action_basic_strategy():
    global dealer_hand
    global deck
    global player_hand

    global split_hands
    global surrender_allowed

    # H = Hit, S = Stand, D = Double down, Sur = Surrender
    # P = Split

    # Note to iterate over 2 -> 10, and then go back to 1.

    if surrender_allowed:
        hard_decision_dict = {5: ["H"]*10,
                              6: ["H"] * 10,
                              7: ["H"] * 10,
                              8: ["H"]*3 + ["D"]*2 + ["H"]*5,
                              9: ["D"]*5 + ["H"]*5,
                              10: ["D"]*8 + ["H"]*2,
                              11: ["D"]*10,
                              12: ["H"]*2 + ["S"]*3 + ["H"]*5,
                              13: ["S"]*5 + ["H"]*5,
                              14: ["S"]*5 + ["H"]*5,
                              15: ["S"]*5 + ["H"]*4 + ["Sur"] *1,
                              16: ["S"]*5 + ["H"]*3 + ["Sur"] *2,
                              17: ["S"]*9 + ["Sur"] *1,
                              18: ["S"]*10,
                              19: ["S"]*10,
                              20: ["S"]*10,
                              21: ["S"]*10,
                              }

        # If ace in the hand (AND IT'S WORTH 11, NOT 1)
        soft_decision_dict = {
                                12: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
                                13: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
                                14: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
                                15: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
                                16: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
                                17: ["D"]*5 + ["H"]*5,
                                18: ["S"]*1 + ["D"]*4 + ["S"]*2 + ["H"] * 3,
                                19: ["S"] * 4 + ["D"] * 1 + ["S"] * 5,
                                20: ["S"] * 10,
                                21: ["S"] * 10}

        split_decision_dict = {
            2: ["P"] * 6 + ["H"] * 4,
            3: ["P"] * 7 + ["H"] * 3,
            4: ["H"] * 2 + ["P"] * 3 + ["H"] * 5,
            5: ["D"]*8 + ["H"]*2,
            6: ["P"] * 6 + ["H"] * 4,
            7: ["P"]*7 + ["H"]*1 + ["Sur"] *2,
            8: ["P"] * 10,
            9: ["P"] * 5 + ["S"]*1 + ["P"]*2 + ["S"]*1 + ["P"]*1,
            10: ["S"]*10,
            1: ["P"] * 10
        }
    else:
        hard_decision_dict = {5: ["H"] * 10,
                              6: ["H"] * 10,
                              7: ["H"] * 10,
                              8: ["H"] * 3 + ["D"] * 2 + ["H"] * 5,
                              9: ["D"] * 5 + ["H"] * 5,
                              10: ["D"] * 8 + ["H"] * 2,
                              11: ["D"] * 10,
                              12: ["H"] * 2 + ["S"] * 3 + ["H"] * 5,
                              13: ["S"] * 5 + ["H"] * 5,
                              14: ["S"] * 5 + ["H"] * 5,
                              15: ["S"] * 5 + ["H"] * 5,
                              16: ["S"] * 5 + ["H"] * 5,
                              17: ["S"] * 10,
                              18: ["S"] * 10,
                              19: ["S"] * 10,
                              20: ["S"] * 10,
                              21: ["S"] * 10,
                              }

        # If ace in the hand (AND IT'S WORTH 11, NOT 1)
        soft_decision_dict = {
            12: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
            13: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
            14: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
            15: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
            16: ["H"] * 2 + ["D"] * 3 + ["H"] * 5,
            17: ["D"] * 5 + ["H"] * 5,
            18: ["S"] * 1 + ["D"] * 4 + ["S"] * 2 + ["H"] * 3,
            19: ["S"] * 4 + ["D"] * 1 + ["S"] * 5,
            20: ["S"] * 10,
            21: ["S"] * 10}

        split_decision_dict = {
            2: ["P"] * 6 + ["H"] * 4,
            3: ["P"] * 7 + ["H"] * 3,
            4: ["H"] * 2 + ["P"] * 3 + ["H"] * 5,
            5: ["D"] * 8 + ["H"] * 2,
            6: ["P"] * 6 + ["H"] * 4,
            7: ["P"] * 7 + ["H"] * 1 + ["S"] * 1 + ["H"] * 1,
            8: ["P"] * 10,
            9: ["P"] * 5 + ["S"] * 1 + ["P"] * 2 + ["S"] * 1 + ["P"] * 1,
            10: ["S"] * 10,
            1: ["P"] * 10
        }

    use_soft = False
    use_hard = False
    use_split = False

    dealer_up_card = dealer_hand[0]  # ace is 11 on dealer always, since is never 1 until dealer starts finishing hand
    hand_val = get_hand_value("Player")
    action = ""

    if hand_val > 21:
        action = "S"
        return action
    else:
        if player_hand[0] == player_hand[1] and len(player_hand) == 2:  # same cards in 2, and only 2 cards in hand
            use_split = True

            action = split_decision_dict[player_hand[0]][dealer_up_card - 2]
            return action
        elif 11 in player_hand:
            #print("11 detected in  player hand", player_hand)
            use_soft = True

            action = soft_decision_dict[hand_val][dealer_up_card - 2]
            return action
        else:
            use_hard = True

            action = hard_decision_dict[hand_val][dealer_up_card - 2]
            return action


def handle_hand_split():
    # Append original hand to split hands
    global split_hands
    global player_hand

    split_card = player_hand[1]
    player_hand.remove(split_card)
    draw_card_main("Player")

    split_hands.append(player_hand)

    player_hand = []
    player_hand.append(split_card)
    draw_card_main("Player")

    split_hands.append(player_hand)

    player_hand = []  # this will throw an error if referenced now, which verifies that split hands is being used properly if no error.


def draw_card_main(who_draw, is_initial_draw = False):
    draw_card_list(who_draw, is_initial_draw)
    modify_hand_value(who_draw)
    get_deck_value_card_counting()  # Get the true count of the deck for card counting


def modify_hand_value(who_draw):
    global player_hand
    global dealer_hand

    if who_draw == "Player":
        if 11 in player_hand and get_hand_value(who_draw) > 21:
            for idx, card in enumerate(player_hand):
                if card == 11:
                    player_hand[idx] = 1


    if who_draw == "Dealer":
        if 11 in dealer_hand and get_hand_value(who_draw) > 21:
            for idx, card in enumerate(dealer_hand):
                if card == 11:
                    dealer_hand[idx] = 1



def draw_card_list(who_draw, is_initial_draw=False):
    # starter_card_list exists to not get rid of 1st drawn card (if it exists)
    global deck
    global player_hand
    global dealer_hand

    if is_initial_draw:
        card_value = get_card_value(random.randint(1, 13), who_draw)  # generate val to determine which card RNG selects

        if deck[card_value] == 0:
            draw_card_list(who_draw, is_initial_draw=False)  # call function again, can't draw this card
        else:
            deck[card_value] -= 1
            if who_draw == "Dealer":
                dealer_hand += [card_value]
            elif who_draw == "Player":
                player_hand += [card_value]


    # Draw another afterwards regardless. If it's initial, then it is 2nd card, otherwise it's 1st card.
    card_value = get_card_value(random.randint(1, 13), who_draw)  # generate val to determine which card RNG selects

    if deck[card_value] == 0:
        draw_card_list(who_draw, is_initial_draw=False)  # call function again, can't draw this card
    else:
        deck[card_value] -= 1
        if who_draw == "Dealer":
            dealer_hand += [card_value]
        elif who_draw == "Player":
            player_hand += [card_value]




def get_hand_value(who_draw):
    global deck
    global player_hand
    global dealer_hand

    hand_val = 0

    if who_draw == "Player":
        for cards in player_hand:
            hand_val += cards
    elif who_draw == "Dealer":
        for cards in dealer_hand:
            hand_val += cards

    return hand_val



def iterate_player_hand(player_strategy):
    # This will tap into the decide module for player actions
    global player_hand
    global dealer_hand
    global deck
    global player_standing
    global did_player_surrender

    global is_DD
    global is_dd_allowed

    global true_count

    hand_val = get_hand_value("Player")

    if player_strategy == "Dealer":

        if hand_val <= 21 and hand_val >= 17:
            print("Player Standing")
            player_standing = True

    elif player_strategy == "Counting":
        action = get_player_action_card_counting()

        #print("Action:", action)

        if action == "H":  # proceed
            player_standing = False
        elif action == "S":
            player_standing = True
        elif action == "D":
            player_standing = False
            if is_dd_allowed:
                is_DD = True
            else:
                is_DD = False
        elif action == "Sur":
            player_standing = True
            did_player_surrender = True
        elif action == "P":
            player_standing = False
            handle_hand_split()

    elif player_strategy == "Basic":
        action = get_player_action_basic_strategy()

        #print("Action:", action)

        if action == "H":  # proceed
            player_standing = False
        elif action == "S":
            player_standing = True
        elif action == "D":
            player_standing = False
            if is_dd_allowed:
                is_DD = True
            else:
                is_DD = False
        elif action == "Sur":
            player_standing = True
            did_player_surrender = True
        elif action == "P":
            player_standing = False
            handle_hand_split()



def assign_cash_winning_value(who_won):
    global is_DD

    if is_DD:
        cash_value = 200
    else:
        cash_value = 100

    if who_won == "Dealer":
        cash_value *= -1
    elif who_won == "Player":
        is_DD = False  # reset it back down to normal after DD
    else:
        cash_value = 0

    return cash_value


# If at/below 21, then compare hand vs dealer to see draw vs win.
# Check if dealer has finished first.
def decide_gamestate(is_initial_draw=False):
    global deck
    global player_hand
    global dealer_hand
    global player_standing
    global dealer_is_finished
    global did_player_surrender

    global cash_winning_arr  # necessary for doubles

    game_winner = "None"

    if not did_player_surrender:


        # Check if 21 met first (for both hands just in case), then check
        if get_hand_value("Dealer") == 21 or get_hand_value("Player") == 21:

            # Check for 2 21's
            if get_hand_value("Dealer") == 21 and get_hand_value("Player") == 21:
                game_winner = "Draw"
                return game_winner  # End the game right now.

            # Player 21, dealer not 21.
            if get_hand_value("Player") == 21:
                if dealer_is_finished:
                    game_winner = "Player"
                    cash_winning_arr.append(assign_cash_winning_value(game_winner))
                    return game_winner
                else:
                    player_standing = True  # If player has 21, then stand regardless.

            # Dealer has 21 (potentially hidden), Player does not
            if get_hand_value("Dealer") == 21:
                if is_initial_draw:
                    if dealer_hand[1] == 11:  #If the dealer has an ace exposed he will check for blackjack, in which case all player hands lose, except another blackjack.
                        game_winner = "Dealer"
                        cash_winning_arr.append(assign_cash_winning_value(game_winner))
                        return game_winner  # Regardless if insurance taken, dealer wins here, since he has 21 and player doesn't.

                    else:
                        game_winner = "Dealer"
                        cash_winning_arr.append(assign_cash_winning_value(game_winner))
                        return game_winner  # only offer insurance on up aces, so end game as dealer won and both players didn't trigger an endgame from 2 blackjacks.

                else:
                    game_winner = "Dealer"
                    cash_winning_arr.append(assign_cash_winning_value(game_winner))
                    return game_winner

        # Check for busts
        # If both the dealer and player bust, the player loses.
        # If either the player or the dealer exceed 21 or “bust” the hand automatically loses.

        # So, if player exceeds 21 at any point, instant loss.

        elif get_hand_value("Dealer") > 21 or get_hand_value("Player") > 21:
            if get_hand_value("Player") > 21:
                game_winner = "Dealer"
                cash_winning_arr.append(assign_cash_winning_value(game_winner))
                return game_winner

            # Player not at 21, but dealer is
            if get_hand_value("Dealer") > 21:
                game_winner = "Player"
                cash_winning_arr.append(assign_cash_winning_value(game_winner))
                return game_winner

        else:  # No one has busted their hand nor does anyone have 21. Both situations have been accounted for.
            if dealer_is_finished:  # dealer will only be finished once player stands.
                if get_hand_value("Dealer") > get_hand_value("Player"):
                    game_winner = "Dealer"
                    cash_winning_arr.append(assign_cash_winning_value(game_winner))
                    return game_winner
                elif get_hand_value("Dealer") < get_hand_value("Player"):
                    game_winner = "Player"
                    cash_winning_arr.append(assign_cash_winning_value(game_winner))
                    return game_winner
                elif get_hand_value("Dealer") == get_hand_value("Player"):
                    game_winner = "Draw"
                    cash_winning_arr.append(assign_cash_winning_value(game_winner))
                    return game_winner
            else:
                # Maybe tap into decide module here, but prob not...
                # Regardless, dealer isn't finished, so no one is a winner yet.
                pass
    else:
        pass
        # Player surrendered
        game_winner = "Dealer"
        cash_winning_arr.append(assign_cash_winning_value(game_winner)/2)
        return game_winner

    cash_winning_arr.append(assign_cash_winning_value(game_winner))
    return game_winner


# Dealer only draws card at start and at end, so take care of it all here.
def finish_dealer_hand():
    global dealer_hand
    global player_hand
    global deck

    hand_val = get_hand_value("Dealer")
    print("Finishing Dealer hand", str(hand_val), str(dealer_hand))

    if (hand_val <= 21 and hand_val >= 17) or hand_val > 21:
        keep_drawing = False
    else:
        keep_drawing = True

    while keep_drawing:
        draw_card_main("Dealer")
        hand_val = get_hand_value("Dealer")

        if (hand_val <= 21 and hand_val >= 17) or hand_val > 21:
            keep_drawing = False

        print(str(hand_val), str(dealer_hand))

    print("Finished Dealer Hand", str(hand_val), str(dealer_hand))


def play_blackjack(player_strategy):
    global deck
    global player_hand
    global dealer_hand

    global split_hands

    global player_standing
    global dealer_is_finished

    global win_count_dict  # necessary for split hands
    global cash_winning_arr  # necessary for doubles
    global is_DD
    is_DD = False  # reset to false for every hand. In cases of split hands, each hand is handled separately to completion before the decision to DD. So, the DD reset in assigning winnings doesn't overwrite a split -> DD

    global did_player_surrender

    dealer_is_finished = False
    did_player_surrender = False

    player_hand = []
    dealer_hand = []

    split_hands = []

    cash_winning_arr = []  # for DD

    winner_array = []

    player_standing = False

    create_initial_deck()

    true_count = 0

    # on initial draw, no cards are in hand
    draw_card_main(who_draw="Dealer",is_initial_draw=True)
    draw_card_main(who_draw="Player",is_initial_draw=True)

    print("=============================================================")
    print("Initial Hands:")
    print("Player Hand:", str(get_hand_value("Player")), str(player_hand))
    print("Dealer Hand:", str(get_hand_value("Dealer")), str(dealer_hand))

    # Now, there is a dealer with 2 cards and a player with 2 cards. Check if winner exists after every draw
    winner_array.append(decide_gamestate(is_initial_draw=True))

    # Decide what to do using the strategy. Does player want to stand on initial draw?
    iterate_player_hand(player_strategy)

    # If player has given up already, then resolve it now to save computing time
    if did_player_surrender:

        # Handle bug that occurs if dealer has 21 on initial draw AND player surrenders
        if get_hand_value("Dealer") == 21:
            print(cash_winning_arr)
            return winner_array
        else:
            winner_array.append(decide_gamestate())
            print(cash_winning_arr)
            return winner_array


    # Note that if a split occurs, split_hands will hold both the original hand and the split hands.
    # Treat each split hand as a unique hand and solve the gamestate separately. But, only solve Dealer once
    if len(split_hands) > 0:

        initial_dealer_hand = dealer_hand
        split_counter = 1

        final_dealer_hand = []

        for split_hand in split_hands:
            player_hand = split_hand
            player_standing = False  # reset condition

            dealer_hand = initial_dealer_hand  # reset dealer hand to initial at every step to not break logic.

            split_winner_array = []
            temp_split_winner_array = []

            # Initial Draw happened, now do player decisions/hands before standing when happy and deciding the game
            while not player_standing and "Player" not in split_winner_array and "Dealer" not in split_winner_array and "Draw" not in split_winner_array:
                draw_card_main(who_draw="Player")  # Draw a new card
                print("Split Player Hand:", str(get_hand_value("Player")), str(player_hand))
                iterate_player_hand(player_strategy)  # Update player_standing value here
                # Only assign 1 win in this case
                if did_player_surrender:
                    split_winner_array.append(decide_gamestate())
                    cash_winning_arr.append(assign_cash_winning_value("Dealer")/2)

                    player_standing = True


                split_winner_array.append(decide_gamestate())  # Update winner value here (bust, for instance)

            if not did_player_surrender:
                if "Player" in split_winner_array or "Dealer" in split_winner_array or "Draw" in split_winner_array:
                    pass  # already assigned win
                else:  # decide final hand with dealer
                    if player_standing:
                        if split_counter == 1 or len(final_dealer_hand) == 0:  # do if 1st iteration or if hasn't been done yet
                            finish_dealer_hand()
                            final_dealer_hand = dealer_hand  # on 1st split hand (original hand), finalize the dealer's hand
                        else:
                            dealer_hand = final_dealer_hand

                        dealer_is_finished = True  # Only set this after player is done, otherwise logic will break (even if dealer starts 21)

                        split_winner_array.append(decide_gamestate())  # Check for winner after both hands finish

            winner_array += split_winner_array  # quickly append the split winners onto the main array and then reset the split winners.
            split_counter += 1

    else:
        # Initial Draw happened, now do player decisions/hands before standing when happy and deciding the game
        while not player_standing and "Player" not in winner_array and "Dealer" not in winner_array and "Draw" not in winner_array:
            draw_card_main(who_draw="Player")  # Draw a new card
            print("Player Hand:", str(get_hand_value("Player")), str(player_hand))
            iterate_player_hand(player_strategy)  # Update player_standing value here
            # Only assign 1 win in this case
            if did_player_surrender:
                winner_array.append(decide_gamestate())
                player_standing = True
            else:
                winner_array.append(decide_gamestate())  # Update winner value here (bust, for instance)

        if not did_player_surrender:
            if "Player" in winner_array or "Dealer" in winner_array or "Draw" in winner_array:
                pass  # already assigned win
            else:  # decide final hand with dealer
                if player_standing:  # Finish off the dealers hand after player stands.
                    finish_dealer_hand()
                    dealer_is_finished = True  # Only set this after player is done, otherwise logic will break (even if dealer starts 21)

                    winner_array.append(decide_gamestate())  # Check for winner after both hands finish

        # If wins, add to statistics module

        # If continue, grab from decision module here

    print(cash_winning_arr)
    return winner_array
    # return who won Dealer or Player


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


if __name__ == "__main__":
    # For stat gathering:
    stat_cash_winning_mean_arr = []
    stat_win_count_dicts = []
    stat_winrate_arr = []

    is_dd_allowed = True
    surrender_allowed = True
    card_methodology = "Hi-Lo 1"  # "Hi-Opt 1" as alternative

    # player strategy list of possible choices
    # Dealer is something of a baseline winrate, just by playing by fixed rules. Exposes house advantage.
    player_strategy_list = ["Dealer", "Basic", "Counting"]

    player_strategy = player_strategy_list[1]
    games_to_play = 150000 # 100000
    num_of_sims = 50  # 30

    print(f"Running {num_of_sims} simulations, with {games_to_play} games to play in each.")
    print("Disabling print")
    blockPrint()

    for j in range(0, num_of_sims):
        # Reset between simulations
        cash_winnings = 0
        win_count_dict = {"Dealer": 0,
                          "Player": 0,
                          "Draw": 0}

        cash_winning_arr = []  # for DD
        is_DD = True

        deck = {}
        player_hand = []
        dealer_hand = []

        split_hands = []

        did_player_surrender = False

        cash_winnings = 0
        current_bet = 100
        doubledown_count = 0

        winrate_arr = []
        total_won_hands = 0



        for i in range(0, games_to_play):
            true_count = 0
            winner_arr = play_blackjack(player_strategy)

            print(winner_arr)

            for winners in winner_arr:
                if winners != "None":  # don't finalize None results
                    win_count_dict[winners] += 1

            hand_winning = cash_winnings  # Gets initial cumulative value

            for cash_winning in cash_winning_arr:  # Contains list of cash winnings (necessary for splits) - tracks DD/surrender per hand.
                cash_winnings += cash_winning

            hand_winning = cash_winnings - hand_winning  # Updates the hand winning by subtracting 2 cumulative values

            # Print after every attempt

            print(win_count_dict)
            print(cash_winnings)

        # Append after every iteration
        total_won_hands = win_count_dict["Player"] + win_count_dict["Dealer"]
        winrate_arr = win_count_dict["Player"]/total_won_hands


        stat_cash_winning_mean_arr.append(cash_winnings / total_won_hands)
        stat_win_count_dicts.append(win_count_dict)
        stat_winrate_arr.append(winrate_arr)

    # Final vals
    print("Enabling Print")
    enablePrint()
    print("Winrate: ",stat_winrate_arr)
    print("Mean cash: ",stat_cash_winning_mean_arr)
    print(stat_win_count_dicts)

    #print(drawn_cards)
