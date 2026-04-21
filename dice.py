import random

# Game state
ante = 0
alive = True
total = 0


def roll_dice(num_dice):
    """Roll num_dice dice and return the list of results."""
    rolls = [random.randint(1, 6) for _ in range(num_dice)]
    return rolls


def parse_input(input_string):
    """Validate user input for dice roll count (1-6)."""
    if input_string.strip() in {"1", "2", "3", "4", "5", "6"}:
        return int(input_string)
    print("Please enter a number from 1 to 6.")
    return parse_input(input("How many dice (d6) do you want to roll? "))




def roll_d6():
    """Roll user-defined amount of d6 and add to total."""
    global total
    num_dice = input("How many dice (d6) do you want to roll? ")
    num_dice = parse_input(num_dice)
    rolls = roll_dice(num_dice)
    subtotal = sum(rolls)
    total += subtotal
    print(f"You rolled: {num_dice} d6 with results {rolls} = {subtotal}")
    return total


def endstate():
    """Check game state and determine if game continues."""
    global ante, alive, total
    print(f"Your current total is: {total}")
    if total >= 10 * ante:
        print("You have successfully powered the Chaos Machine! Ante up!")
        total = 0
        ante += 1
    elif total <= 0:
        print("The Chaos Machine has backfired and destroyed itself! You lose!")
        alive = False
    else:
        print("The Chaos Machine is unstable. Try again to power it up or risk it backfiring!")


def main():
    """Main game loop for Chaos Machine."""
    global ante, alive, total

    print("Welcome to the Chaos Machine!")

    while alive:
        print(f"Ante: {ante}")
        if ante == 1:
            print(f"You need to reach at least {10 * ante} to power the Chaos Machine. "
                  "The amount increases with each successful round. Good luck!")
        else:
            print(f"You need to reach at least {10 * ante} to power the Chaos Machine.")
        input("Press Enter to continue...")
        roll_d6()
        input("Press Enter to continue...")
        endstate()


if __name__ == "__main__":
    ante = 1
    total = 0
    alive = True
    main()
