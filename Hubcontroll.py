"""
Hubcontroll - Main game controller for SKooKS game system
Manages map traversal, character rosters, and game state
"""
import time
import datetime
import random

# ============================================================================
# CONSTANTS
# ============================================================================
MAP_SIZE = 10
MAX_COORD = 9
FOREST_ENTRY = (1, 8)

# Character options
GENDERS = ['Male', 'Female', 'Non-Binary', 'Trans', 'Other']
CLASSES = ['Artificer', 'Bard', 'Chivalry', 'Deacon', 'Ebberfolk', 'Falconeer', 'Gardener', 'Hermetic']
CLASS_INFO = {
    'Artificer': {'locked': False, 'hint': None},
    'Bard': {'locked': False, 'hint': None},
    'Chivalry': {'locked': False, 'hint': None},
    'Deacon': {'locked': False, 'hint': None},
    'Ebberfolk': {'locked': False, 'hint': None},
    'Falconeer': {'locked': False, 'hint': None},
    'Gardener': {'locked': True, 'hint': '"My Patch"'},
    'Hermetic': {'locked': True, 'hint': '"A lone tower"'}
}
RACES = ['Human', 'Beastfolk', 'Reptoids', 'Demihuman', 'Imp', 'Fae', 'Chimera', 'Automaton']

# Race base stats and max ages
RACE_STATS = {
    'Human': {'LV': 3, 'TR': 3, 'HN': 3, 'VL': 3, 'max_age': 80, 'hint': None},
    'Beastfolk': {'LV': 4, 'TR': 3, 'HN': 3, 'VL': 2, 'max_age': 60, 'hint': None},
    'Reptoids': {'LV': 3, 'TR': 4, 'HN': 4, 'VL': 1, 'max_age': 60, 'hint': None},
    'Demihuman': {'LV': 4, 'TR': 3, 'HN': 2, 'VL': 3, 'max_age': 70, 'hint': None},
    'Imp': {'LV': 1, 'TR': 4, 'HN': 4, 'VL': 3, 'max_age': 100, 'hint': None},
    'Fae': {'LV': 4, 'TR': 1, 'HN': 3, 'VL': 4, 'max_age': 100, 'hint': None},
    'Chimera': {'LV': 5, 'TR': 1, 'HN': 5, 'VL': 1, 'max_age': 30, 'locked': True, 'hint': 'Deep in the woods, a beast'},
    'Automaton': {'LV': 1, 'TR': 5, 'HN': 1, 'VL': 5, 'max_age': 200, 'locked': True, 'hint': 'What an odd device'}
}

# Available races and classes (unlocked by default)
AVAILABLE_RACES = ['Human', 'Beastfolk', 'Reptoids', 'Demihuman', 'Imp', 'Fae']
AVAILABLE_CLASSES = [name for name, details in CLASS_INFO.items() if not details['locked']]

# Player information
PLAYER_NAME = 'Unknown Adventurer'

# Game maps
WORLD_MAP = [
    ['▒', '≈', '⌂', '▒', '░', '░', '░', '░', '░', '░'],
    ['▒', '≈', '≈', '▒', '░', '░', '░', '░', '░', '░'],
    ['▒', '▒', '▲', '▲', '▒', '▒', '░', '░', '░', '░'],
    ['▒', '▒', '▲', '▲', '▒', '▒', '▒', '░', '🍆', '░'],
    ['▒', '▒', '▒', '≈', '▒', '▒', '▒', '▒', '░', '░'],
    ['▒', '▒', '▒', '≈', '≈', '▒', '▒', '▒', '▒', '░'],
    ['▒', '🌳', '🌳', '▒', '≈', '▒', '▒', '▒', '▒', '▓'],
    ['🌳', '🌳', '🌳', '🌳', '▓', '≈', '≈', '≈', '≈', '▓'],
    ['▓', '🌳', '▓', '▓', '▓', '⌂', '▓', '▓', '▓', '≈'],
    ['▓', '▓', '▓', '▓', '▓', '▓', '▓', '▓', '▓', '▓']
]

FOREST_MAP = [
    ['🌳'] * 10,
    ['🌳'] * 10,
    ['🌳'] * 10,
    ['🌳'] * 10,
    ['🌳', '🌳', '🌳', '🌳', '🌳', '▓', '▓', '▓', '▓', '🌳'],
    ['🌳', '🌳', '🌳', '🌳', '▓', '▓', '🌳', '▓', '▓', '🌳'],
    ['🌳', '🌳', '🌳', '🌳', '🌳', '▓', '🌳', '▓', '🌳', '🌳'],
    ['🌳', '🌳', '🌳', '🌳', '🌳', '▓', '▓', '🌳', '🌳', '🌳'],
    ['🌳', '🌳', '🌳', '🌳', '▓', '▓', '▓', '🌳', '🌳', '🌳'],
    ['🌳', '🌳', '🌳', '▓', '▓', '▓', '▓', '▓', '🌳', '🌳']
]

PLAYER_CHAR = '☺'
FOREST_CHAR = '🌳'
TREE_BLOCKING_CHAR = '🌳'

# ============================================================================
# GAME STATE
# ============================================================================
class GameState:
    """Central game state management"""
    def __init__(self):
        self.world = 'Default'
        self.pos_x = 5
        self.pos_y = 4
        self.travel_direction = 'Null'
        self.is_running = True
        self.in_forest = False
        self.selected_party = []  # List of character indices from roster
        
    def reset_position(self):
        """Reset player position to default starting location"""
        self.pos_x = 5
        self.pos_y = 4
        
    def get_position(self):
        """Return current position as tuple"""
        return (self.pos_x, self.pos_y)
        
    def set_party(self, party_indices):
        """Set the selected party (up to 4 characters)"""
        self.selected_party = party_indices[:4]  # Max 4 characters
        
    def get_party_info(self, roster):
        """Get detailed info for all party members"""
        party_info = []
        for idx in self.selected_party:
            if idx < len(roster.names):
                party_info.append(roster.get_character(roster.names[idx]))
        return party_info


class CharacterRoster:
    """Manage game character roster with stats and memorial system"""
    def __init__(self):
        self.names = []
        self.ages = []
        self.classes = []
        self.races = []
        self.genders = []
        self.levels = []

        # Stats: Love(LV), Trust(TR), Honour(HN), Value(VL)
        self.love_stats = []    # Vitality - hitpoints and mana
        self.trust_stats = []   # Resolve - damage resistance + strength
        self.honour_stats = []  # Nuance - dexterity + focus
        self.value_stats = []   # Learnedness - intellect + wisdom

        # Derived stats
        self.hitpoints = []
        self.max_hitpoints = []
        self.max_ages = []

        # Memorial system for deceased characters
        self.catacomb = []  # List of deceased character records
        
        # Unlocked races and classes tracking
        self.unlocked_races = AVAILABLE_RACES.copy()
        self.unlocked_classes = AVAILABLE_CLASSES.copy()

    def unlock_race(self, race):
        """Unlock a previously locked race"""
        if race in RACE_STATS and race not in self.unlocked_races:
            if RACE_STATS[race].get('locked', False):
                self.unlocked_races.append(race)
                RACE_STATS[race]['locked'] = False
                print(f"🎉 Race unlocked: {race}!")
                return True
        return False

    def unlock_class(self, class_name):
        """Unlock a previously locked class"""
        if class_name in CLASS_INFO and class_name not in self.unlocked_classes:
            if CLASS_INFO[class_name].get('locked', False):
                self.unlocked_classes.append(class_name)
                CLASS_INFO[class_name]['locked'] = False
                print(f"🎉 Class unlocked: {class_name}!")
                return True
        return False

    def calculate_base_stats(self, race):
        """Calculate base stats from race"""
        base = RACE_STATS[race]
        return {
            'LV': base['LV'],
            'TR': base['TR'],
            'HN': base['HN'],
            'VL': base['VL'],
            'max_age': base['max_age']
        }

    def add_character(self, name, age, char_class, race, gender):
        """Add a new character to roster with calculated stats"""
        stats = self.calculate_base_stats(race)

        self.names.append(name)
        self.ages.append(age)
        self.classes.append(char_class)
        self.races.append(race)
        self.genders.append(gender)
        self.levels.append(1)

        # Base stats
        self.love_stats.append(stats['LV'])
        self.trust_stats.append(stats['TR'])
        self.honour_stats.append(stats['HN'])
        self.value_stats.append(stats['VL'])

        # Derived stats
        hp = stats['LV'] * 10  # Hitpoints = LV * 10
        self.hitpoints.append(hp)
        self.max_hitpoints.append(hp)
        self.max_ages.append(stats['max_age'])

    def remove_character(self, name, cause_of_death="Unknown"):
        """Remove character and add to memorial"""
        if name in self.names:
            idx = self.names.index(name)

            # Create memorial record
            memorial = {
                'name': self.names[idx],
                'age': self.ages[idx],
                'class': self.classes[idx],
                'race': self.races[idx],
                'gender': self.genders[idx],
                'level': self.levels[idx],
                'cause_of_death': cause_of_death,
                'date_of_death': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'stats': {
                    'LV': self.love_stats[idx],
                    'TR': self.trust_stats[idx],
                    'HN': self.honour_stats[idx],
                    'VL': self.value_stats[idx]
                }
            }
            self.catacomb.append(memorial)

            # Remove from active roster
            self.names.pop(idx)
            self.ages.pop(idx)
            self.classes.pop(idx)
            self.races.pop(idx)
            self.genders.pop(idx)
            self.levels.pop(idx)
            self.love_stats.pop(idx)
            self.trust_stats.pop(idx)
            self.honour_stats.pop(idx)
            self.value_stats.pop(idx)
            self.hitpoints.pop(idx)
            self.max_hitpoints.pop(idx)
            self.max_ages.pop(idx)
            return True
        return False

    def get_character(self, name):
        """Get character info by name"""
        if name in self.names:
            idx = self.names.index(name)
            return {
                'name': self.names[idx],
                'age': self.ages[idx],
                'class': self.classes[idx],
                'race': self.races[idx],
                'gender': self.genders[idx],
                'level': self.levels[idx],
                'stats': {
                    'LV': self.love_stats[idx],
                    'TR': self.trust_stats[idx],
                    'HN': self.honour_stats[idx],
                    'VL': self.value_stats[idx]
                },
                'hitpoints': self.hitpoints[idx],
                'max_hitpoints': self.max_hitpoints[idx],
                'max_age': self.max_ages[idx]
            }
        return None

    def display_character(self, char_dict):
        """Pretty print character info with stats"""
        name = char_dict['name']
        border = f"|{'─' * (len(name) + 6)}|"
        print(f"\t{border}")
        print(f"\t| {name}:")
        print(f"\t{border}")
        print(f"\t| Age: {char_dict['age']:.1f} years")
        print(f"\t| Class: {char_dict['class']}")
        print(f"\t| Race: {char_dict['race']}")
        print(f"\t| Gender: {char_dict['gender']}")
        print(f"\t| Level: {char_dict['level']}")
        print(f"\t| HP: {char_dict['hitpoints']}/{char_dict['max_hitpoints']}")
        print(f"\t| Max Age: {char_dict['max_age']}")
        print(f"\t|")
        print(f"\t| STATS:")
        print(f"\t| Love (LV): {char_dict['stats']['LV']} - Vitality")
        print(f"\t| Trust (TR): {char_dict['stats']['TR']} - Resolve")
        print(f"\t| Honour (HN): {char_dict['stats']['HN']} - Nuance")
        print(f"\t| Value (VL): {char_dict['stats']['VL']} - Learnedness")
        print(f"\t{border}\n")

    def display_memorial(self):
        """Display the catacomb of deceased characters"""
        if not self.catacomb:
            print("\nThe catacomb is empty. No characters have passed on yet.\n")
            return

        print("\n" + "="*60)
        print("           🪦 THE CATACOMB 🪦")
        print("     Memorial for the Departed")
        print("="*60)

        for memorial in self.catacomb:
            print(f"\n✝ {memorial['name']} ✝")
            print(f"   Class: {memorial['class']} | Race: {memorial['race']}")
            print(f"   Age: {memorial['age']:.1f} | Gender: {memorial['gender']}")
            print(f"   Level: {memorial['level']}")
            print(f"   Cause: {memorial['cause_of_death']}")
            print(f"   Date: {memorial['date_of_death']}")
            print(f"   Final Stats - LV:{memorial['stats']['LV']} TR:{memorial['stats']['TR']} HN:{memorial['stats']['HN']} VL:{memorial['stats']['VL']}")
            print("-" * 40)

        print("="*60 + "\n")

    def is_empty(self):
        """Check if roster is empty"""
        return len(self.names) == 0

    def advance_time(self, time_unit, amount):
        """Advance time for all characters"""
        if self.is_empty():
            print("There are no players!")
            return

        try:
            amount = float(amount)
            if amount <= 0:
                print("Cancelled")
                return

            # Convert to years
            if time_unit.lower() == 'months':
                years_to_add = amount * 0.083  # 1 month ≈ 0.083 years
            else:  # years
                years_to_add = amount

            print(f"Advancing {amount} {time_unit}... ({years_to_add:.3f} years)")
            time.sleep(1.0)

            indices_to_remove = []
            for i, name in enumerate(self.names):
                old_age = self.ages[i]
                self.ages[i] += years_to_add

                # Check for natural death (max age)
                if self.ages[i] >= self.max_ages[i]:
                    print(f"{name} has reached their maximum age of {self.max_ages[i]} and passed away peacefully.")
                    indices_to_remove.append((i, "Natural causes (old age)"))
                    continue

                # Check for HP death (aging damage scales with max HP)
                aging_damage = int(self.max_hitpoints[i] * 0.01 * years_to_add)  # 1% of max HP per year
                self.hitpoints[i] -= aging_damage

                if self.hitpoints[i] <= 0:
                    print(f"{name} has succumbed to the ravages of time and passed away.")
                    indices_to_remove.append((i, "Natural causes (aging)"))
                    continue

                # Age description
                if years_to_add >= 1:
                    print(f"{name} aged from {old_age:.1f} to {self.ages[i]:.1f} years.")
                else:
                    print(f"{name} aged slightly from {old_age:.1f} to {self.ages[i]:.1f} years.")

            # Remove deceased characters (in reverse to preserve indices)
            for idx, cause in reversed(indices_to_remove):
                name = self.names[idx]
                self.remove_character(name, cause)

        except ValueError:
            print("Invalid input. Operation cancelled.")


# ============================================================================
# MAP FUNCTIONS
# ============================================================================
def display_map(game_map, state, roster):
    """Display current map with player position and party info"""
    print('   N')
    print('W =╬= E\t  [Coordinates: {},{} | Area: {}]'.format(
        state.pos_y + 1, state.pos_x + 1, state.world))
    print('   S')
    
    for row in game_map:
        for item in row:
            print(item, end='\t')
        print()
    
    # Display party status
    if state.selected_party:
        print("\n🎒 PARTY STATUS:")
        party_info = state.get_party_info(roster)
        for i, char in enumerate(party_info):
            status = "❤️" if char['hitpoints'] > char['max_hitpoints'] * 0.5 else "💔"
            print(f"  {i+1}. {char['name']} {status} HP:{char['hitpoints']}/{char['max_hitpoints']}")
    print()


def get_map_input():
    """Get compass direction from player"""
    return input('Move (N/E/S/W) or M for menu: ')


def is_valid_move(new_x, new_y):
    """Validate move is within map bounds"""
    return 0 <= new_x <= MAX_COORD and 0 <= new_y <= MAX_COORD


def handle_forest_movement(direction, state):
    """Handle movement within forest"""
    if direction in ['n', 'N']:
        state.travel_direction = 'North'
        if state.pos_y > 0:
            state.pos_y -= 1
        else:
            print("You can't travel any farther in this direction")
    elif direction in ['e', 'E']:
        state.travel_direction = 'East'
        if state.pos_x < MAX_COORD:
            state.pos_x += 1
        else:
            print("You can't travel any farther in this direction")
    elif direction in ['s', 'S']:
        state.travel_direction = 'South'
        if state.pos_y < MAX_COORD:
            state.pos_y += 1
        else:
            print("You can't travel any farther in this direction")
    elif direction in ['w', 'W']:
        state.travel_direction = 'West'
        if state.pos_x <= 0 and state.pos_y <= 5:
            state.pos_x, state.pos_y = 0, 6
            state.world = 'Default'
            state.in_forest = False
        elif state.pos_x == 0 and state.pos_y > 5:
            state.pos_x, state.pos_y = 0, 8
            state.world = 'Default'
            state.in_forest = False
        else:
            state.pos_x -= 1
    elif direction in ['m', 'M']:
        return 'menu'


def handle_world_movement(direction, state):
    """Handle movement in default world"""
    if direction in ['n', 'N']:
        state.travel_direction = 'North'
        if state.pos_y > 0:
            state.pos_y -= 1
        else:
            print("You can't travel any farther in this direction")
    elif direction in ['e', 'E']:
        state.travel_direction = 'East'
        if state.pos_x < MAX_COORD:
            state.pos_x += 1
        else:
            print("You can't travel any farther in this direction")
    elif direction in ['s', 'S']:
        state.travel_direction = 'South'
        if state.pos_y < MAX_COORD:
            state.pos_y += 1
        else:
            print("You can't travel any farther in this direction")
    elif direction in ['w', 'W']:
        state.travel_direction = 'West'
        if state.pos_x > 0:
            state.pos_x -= 1
        else:
            print("You can't travel any farther in this direction")
    elif direction in ['m', 'M']:
        return 'menu'


def move_player(current_map, state):
    """Handle player movement on current map"""
    # Clear old player position
    current_map[state.pos_y][state.pos_x] = WORLD_MAP[state.pos_y][state.pos_x] \
        if state.world == 'Default' else '🌳'
    
    # Get input
    direction = get_map_input()
    
    # Handle movement based on current world
    if state.world == 'Forest':
        handle_forest_movement(direction, state)
    else:
        result = handle_world_movement(direction, state)
        if result == 'menu':
            return 'menu'
    
    # Place player on new position
    current_map[state.pos_y][state.pos_x] = '☺'
    return 'continue'


def check_collision(current_map, state):
    """Check if player hit an obstacle and bounce back"""
    if (current_map[state.pos_y][state.pos_x] == '🌳' and 
        state.get_position() != FOREST_ENTRY):
        print('ouch!')
        
        # Reverse last move
        if state.travel_direction == 'North':
            state.pos_y += 1
        elif state.travel_direction == 'South':
            state.pos_y -= 1
        elif state.travel_direction == 'East':
            state.pos_x -= 1
        elif state.travel_direction == 'West':
            state.pos_x += 1
        
        return False
    return True


def map_main(game_state, roster):
    """Main map traversal loop"""
    current_map = [row[:] for row in WORLD_MAP]  # Copy map
    
    # Place player on initial position
    current_map[game_state.pos_y][game_state.pos_x] = '☺'
    
    while game_state.is_running:
        # Check if entering forest
        if game_state.get_position() == FOREST_ENTRY:
            game_state.world = 'Forest'
            game_state.in_forest = True
            current_map = [row[:] for row in FOREST_MAP]  # Copy forest map
            current_map[game_state.pos_y][game_state.pos_x] = '☺'
            return
        
        # Display current map
        display_map(current_map, game_state, roster)
        
        # Check for collision
        if not check_collision(current_map, game_state):
            continue
        
        # Place player and get input
        current_map[game_state.pos_y][game_state.pos_x] = '☺'
        result = move_player(current_map, game_state)
        
        if result == 'menu':
            return


# ============================================================================
# CHARACTER ROSTER FUNCTIONS
# ============================================================================
def display_roster_menu(roster):
    """Display character roster management menu"""
    print("\n#----------------------------------#")
    print("  ADD [+]")
    print("  REMOVE [-]")
    print("  DISPLAY THE ROSTER [t]")
    print("  DISPLAY RANDOM PLAYER [r]")
    print("  DISPLAY SPECIFIC PLAYER [p]")
    print("  AGE [a]")
    print("  UNLOCK CONTENT [u]")
    print("  STATS INFO [s]")
    print("  VIEW CATACOMB [c]")
    print("  EXIT [exit]")
    print("#----------------------------------#")
    print(f"  {datetime.datetime.now()}")
    return input("_>| ").strip()


def unlock_content_menu(roster):
    """Menu for unlocking locked races and classes"""
    print("\n#----------------------------------#")
    print("  UNLOCK CONTENT MENU")
    print("#----------------------------------#")
    
    locked_items = []
    for race, data in RACE_STATS.items():
        if data.get('locked', False):
            locked_items.append(('race', race, data.get('hint', 'Locked race')))
    for cls, data in CLASS_INFO.items():
        if data.get('locked', False):
            locked_items.append(('class', cls, data.get('hint', 'Locked class')))
    
    if not locked_items:
        print("All locked content has been unlocked!")
        return
    
    for i, (item_type, _, hint) in enumerate(locked_items, 1):
        label = 'Race' if item_type == 'race' else 'Class'
        print(f"  {i}. {label} hint: {hint}")
    
    print("  0. Cancel")
    print("#----------------------------------#")
    
    try:
        choice = int(input("Select item to unlock: ").strip())
        if choice == 0:
            return
        elif 1 <= choice <= len(locked_items):
            item_type, name, _ = locked_items[choice - 1]
            if item_type == 'race':
                roster.unlock_race(name)
            else:
                roster.unlock_class(name)
            print(f"Successfully unlocked {name}!")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a number.")


def select_from_list(options, prompt="Select option:"):
    """Generic function to select from a list of options"""
    while True:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        print("(Type 'cancel' to cancel character creation)")
        
        choice = input("\nEnter number or 'cancel': ").strip()
        if choice.lower() == 'cancel':
            return None
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Please enter a number or 'cancel'.")


def select_race(roster):
    """Select race with locked race hints for locked content"""
    while True:
        print("\nSelect Race:")
        all_races = list(RACE_STATS.keys())
        
        for i, race in enumerate(all_races, 1):
            if race in roster.unlocked_races:
                print(f"  {i}. {race}")
            else:
                print(f"  {i}. 🔒 {RACE_STATS[race].get('hint', 'Locked race')}")
        
        print("\nNote: Locked races are hidden until unlocked.")
        print("(Type 'cancel' to cancel character creation)")
        
        choice = input("\nEnter number or 'cancel': ").strip()
        if choice.lower() == 'cancel':
            return None
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(all_races):
                selected_race = all_races[choice_num - 1]
                if selected_race not in roster.unlocked_races:
                    print("❌ That race is currently locked. Unlock it before selecting.")
                    continue
                return selected_race
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Please enter a number or 'cancel'.")


def select_class(roster):
    """Select class with locked class hints and unlock handling"""
    while True:
        print("\nSelect Class:")
        all_classes = list(CLASS_INFO.keys())
        
        for i, class_name in enumerate(all_classes, 1):
            if class_name in roster.unlocked_classes:
                print(f"  {i}. {class_name}")
            else:
                print(f"  {i}. 🔒 {CLASS_INFO[class_name].get('hint', 'Locked class')}")
        
        print("\nNote: Locked classes are hidden until unlocked.")
        print("(Type 'cancel' to cancel character creation)")
        
        choice = input("\nEnter number or 'cancel': ").strip()
        if choice.lower() == 'cancel':
            return None
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(all_classes):
                selected_class = all_classes[choice_num - 1]
                if selected_class not in roster.unlocked_classes:
                    print("❌ That class is currently locked. Unlock it before selecting.")
                    continue
                return selected_class
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Please enter a number or 'cancel'.")


def select_gender():
    """Select gender with sub-options for Trans"""
    gender = select_from_list(GENDERS, "Select Gender:")
    
    if gender is None:
        return None

    if gender == "Trans":
        print("\nSpecify Trans identity (e.g., Trans Male, Trans Female, Non-Binary Trans):")
        sub_gender = input("Trans identity: ").strip()
        if sub_gender:
            gender = f"Trans ({sub_gender})"
    elif gender == "Other":
        print("\nSpecify your gender identity (max 20 characters plz):")
        other_gender = input("Gender identity: ").strip()[:20]
        if other_gender:
            gender = other_gender
        else:
            gender = "Other"

    return gender


def add_characters(roster, count=None):
    """Add new characters to roster with multiple choice options"""
    try:
        if count is None:
            count = int(input("How many players to add? \n_>| "))
        if count <= 0:
            print("Operation cancelled")
            return

        for _ in range(count):
            print("\n" + "="*40)
            print("Creating New Character" + " (Player {})".format(len(roster.names) + 1))
            print("="*40)
            print("(Type 'cancel' at any step to cancel the batch)")

            # Character name
            while True:
                name = input("Character name: ").strip()
                if name.lower() == 'cancel':
                    print("Batch creation cancelled.")
                    break
                if not name:
                    print("Name cannot be empty. Please try again.")
                    continue
                break
            if name.lower() == 'cancel':
                break

            # Race selection
            race = select_race(roster)
            if race is None:  # User cancelled race selection
                print("Batch creation cancelled.")
                break
            race_max_age = RACE_STATS[race]['max_age']

            # Age input with validation
            while True:
                age_input = input(f"Starting age (years, max {race_max_age}): ").strip()
                if age_input.lower() == 'cancel':
                    print("Batch creation cancelled.")
                    break
                try:
                    age = float(age_input)
                    if age < 0:
                        print("Age cannot be negative. Setting to 0.")
                        age = 0
                        break
                    if age > race_max_age:
                        print(f"Age cannot exceed the max age for {race} ({race_max_age}). Please try again.")
                        continue
                    break
                except ValueError:
                    print("Invalid age. Please enter a number.")
            if age_input.lower() == 'cancel':
                break

            # Class selection
            char_class = select_class(roster)
            if char_class is None:  # User cancelled class selection
                print("Batch creation cancelled.")
                break

            # Gender selection
            gender = select_gender()
            if gender is None:  # User cancelled gender selection
                print("Batch creation cancelled.")
                break

            roster.add_character(name, age, char_class, race, gender)
            print(f"\n✓ '{name}' added successfully!")
            print(f"  Race: {race} | Class: {char_class} | Gender: {gender}")
            print(f"  Starting Age: {age}")

    except ValueError:
        print("Invalid input. Operation cancelled.")


def remove_character(roster, player_name=None):
    """Remove a character from roster"""
    if player_name is None:
        player_name = PLAYER_NAME
    if roster.is_empty():
        print("There are no players to remove!")
        return

    print("\n[Players:]")
    for name in roster.names:
        print(f"  {name}")

    selection = input("What player would you like to remove? \n_>| ").strip()

    if selection.lower() == "all":
        for name in roster.names[:]:
            roster.remove_character(name, f"smitten by {player_name}")
        print("All players have been removed and memorialized.")
        return

    if selection.lower() == "cancel":
        print("Operation cancelled")
        return

    if selection not in roster.names:
        print("That player does not exist!")
        return

    confirm = input("Are you sure? This is permanent [y/n] \n_>| ").strip().lower()
    if confirm == "y":
        roster.remove_character(selection, f"smitten by {player_name}")
        print(f"Player '{selection}' removed successfully!")
    else:
        print("Operation cancelled")


def display_player(roster):
    """Display specific player info"""
    if roster.is_empty():
        print("There are no players!")
        return
    
    print("\n[Players:]")
    for name in roster.names:
        print(f"  {name}")
    
    player_name = input("Select your player: \n_>| ").strip()
    
    if player_name.lower() == "cancel":
        print("Operation cancelled")
        return
    
    char = roster.get_character(player_name)
    if char:
        roster.display_character(char)
    else:
        print("That player does not exist!")


def display_all_characters(roster):
    """Display entire roster"""
    if roster.is_empty():
        print("There are no players!")
        return
    
    print("\n   _   _   _   _     _   _   _   _   _")
    print("  / \\ / \\ / \\ / \\   / \\ / \\ / \\ / \\ / \\")
    print(" ( t | e | a | m ) ( i | n | f | o | : )")
    print("  \\_/ \\_/ \\_/ \\_/   \\_/ \\_/ \\_/ \\_/ \\_/\n")
    
    for name in roster.names:
        char = roster.get_character(name)
        roster.display_character(char)
        time.sleep(0.85)


def display_random_player(roster):
    """Display random player from roster"""
    if roster.is_empty():
        print("There are no players!")
        return
    
    random_name = random.choice(roster.names)
    char = roster.get_character(random_name)
    print("\nRandom player selected:")
    roster.display_character(char)


def advance_time(roster):
    """Advance time for all characters"""
    if roster.is_empty():
        print("There are no players!")
        return

    print("\nTime Advancement Options:")
    print("  1. Advance by months")
    print("  2. Advance by years")

    choice = input("Select time unit (1-2): ").strip()

    if choice == "1":
        time_unit = "months"
        prompt = "How many months would you like to advance?"
    elif choice == "2":
        time_unit = "years"
        prompt = "How many years would you like to advance?"
    else:
        print("Invalid choice.")
        return

    amount = input(f"{prompt} \n_>| ").strip()
    roster.advance_time(time_unit, amount)


def display_stats_info(roster):
    """Display comprehensive information about the stat system"""
    print("\n" + "="*70)
    print("                    📊 STAT SYSTEM OVERVIEW 📊")
    print("="*70)
    print("""
The stat system in SKooKS represents four fundamental aspects of character development:

╔══════════════════════════════════════════════════════════════════════════════╗
║                               LOVE (LV) - VITALITY                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ • Hitpoints and Mana pool                                                  ║
║ • Physical and magical endurance                                           ║
║ • Resistance to fatigue and exhaustion                                     ║
║ • Base HP = LV × 10                                                        ║
║ • Higher LV = More survivable in combat and exploration                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                             TRUST (TR) - RESOLVE                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ • Damage resistance and physical strength                                  ║
║ • Mental fortitude and willpower                                          ║
║ • Ability to withstand psychological stress                                ║
║ • Combat effectiveness and defensive capabilities                         ║
║ • Higher TR = Better at tanking damage and maintaining composure         ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                            HONOUR (HN) - NUANCE                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ • Dexterity and precision in movement                                      ║
║ • Focus and concentration abilities                                        ║
║ • Social grace and diplomatic skills                                      ║
║ • Technical proficiency and craftsmanship                                  ║
║ • Higher HN = More agile and skilled in complex tasks                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                           VALUE (VL) - LEARNEDNESS                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ • Intellectual capacity and wisdom                                         ║
║ • Magical aptitude and spellcasting power                                  ║
║ • Knowledge accumulation and problem-solving                               ║
║ • Research and innovation capabilities                                    ║
║ • Higher VL = Greater magical power and scholarly achievements           ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    print("="*70)
    print("\nRace stat overview:")
    for race, data in RACE_STATS.items():
        if race in roster.unlocked_races:
            print(f"  {race:<10} │ LV:{data['LV']} TR:{data['TR']} HN:{data['HN']} VL:{data['VL']} │ max age {data['max_age']}")
        else:
            print(f"  🔒 {data.get('hint', 'Locked race')}")
    print("\nLocked races remain hidden until they are unlocked.")
    print("="*70)
    input("\nPress Enter to return to menu...")


def select_party(roster, game_state):
    """Select a party of up to 4 characters for travel"""
    if roster.is_empty():
        print("No characters available! Create some characters first.")
        return False
        
    print("\n" + "="*50)
    print("           🎒 PARTY SELECTION 🎒")
    print("="*50)
    print("Choose up to 4 characters for your adventuring party:")
    print("(Party members will share the same position on the map)")
    print()
    
    # Display available characters
    print("Available Characters:")
    for i, name in enumerate(roster.names):
        char = roster.get_character(name)
        print(f"  {i+1}. {name} (Lv.{char['level']} {char['race']} {char['class']}) - HP: {char['hitpoints']}/{char['max_hitpoints']}")
    
    selected_indices = []
    max_party_size = min(4, len(roster.names))
    
    while len(selected_indices) < max_party_size:
        try:
            choice = input(f"\nSelect character #{len(selected_indices)+1} (1-{len(roster.names)}), or 'done' to finish: ").strip().lower()
            
            if choice == 'done' and len(selected_indices) > 0:
                break
            elif choice == 'done':
                print("You must select at least 1 character for your party!")
                continue
                
            char_num = int(choice) - 1
            if 0 <= char_num < len(roster.names):
                if char_num not in selected_indices:
                    selected_indices.append(char_num)
                    char_name = roster.names[char_num]
                    print(f"✓ Added {char_name} to party")
                else:
                    print("That character is already in your party!")
            else:
                print(f"Please enter a number between 1 and {len(roster.names)}")
                
        except ValueError:
            print("Please enter a valid number or 'done'")
    
    game_state.set_party(selected_indices)
    
    # Display selected party
    print(f"\n🎉 Party assembled! ({len(selected_indices)} members)")
    party_info = game_state.get_party_info(roster)
    for i, char in enumerate(party_info):
        print(f"  {i+1}. {char['name']} - {char['race']} {char['class']} (HP: {char['hitpoints']}/{char['max_hitpoints']})")
    
    input("\nPress Enter to begin your adventure...")
    return True


def manage_roster(roster):
    """Main character roster management loop"""
    print("\n\t     ███████╗██████╗ ███╗   ███╗")
    print("\t     ██╔════╝██╔══██╗████╗ ████║")
    print("\t     ███████╗██████╔╝██╔████╔██║")
    print("\t     ╚════██║██╔══██╗██║╚██╔╝██║")
    print("\t     ███████║██║  ██║██║ ╚═╝ ██║")
    print("\t     ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝")
    print("\t  -SKooKS Roster Manager-\n")
    
    while True:
        choice = display_roster_menu(roster)

        if choice.startswith("+"):
            shortcut = choice[1:].strip()
            if not shortcut:
                add_characters(roster)
            elif shortcut.isdigit():
                # Check if it's compact indices (at least 3 digits) or count
                indices = list(shortcut)
                if len(indices) >= 3:
                    # Compact index-based shortcut: +2343 (no spaces)
                    race_idx = int(indices[0])
                    class_idx = int(indices[1])
                    gender_idx = int(indices[2])
                    
                    # Validate indices
                    if not (1 <= race_idx <= len(RACES)):
                        print("Invalid race index")
                        continue
                    if not (1 <= class_idx <= len(CLASSES)):
                        print("Invalid class index")
                        continue
                    if not (1 <= gender_idx <= len(GENDERS)):
                        print("Invalid gender index")
                        continue
                    
                    race = RACES[race_idx - 1]
                    char_class = CLASSES[class_idx - 1]
                    gender_base = GENDERS[gender_idx - 1]
                    
                    sub_idx = int(indices[3]) if len(indices) > 3 else None
                    age_str = ''.join(indices[4:]) if len(indices) > 4 else None
                    name = None
                    
                    if gender_base == 'Trans':
                        subgenders = ['Male', 'Female', 'Non-Binary', 'Other']
                        if sub_idx is not None:
                            if not (1 <= sub_idx <= len(subgenders)):
                                print("Invalid subgender index")
                                continue
                            sub = subgenders[sub_idx - 1]
                            gender = f"Trans ({sub})"
                        else:
                            print("Subgender index required for Trans")
                            continue
                    else:
                        gender = gender_base
                    
                    # Get age if not provided
                    if age_str is None:
                        race_max_age = RACE_STATS[race]['max_age']
                        while True:
                            age_input = input(f"Starting age (years, max {race_max_age}): ").strip()
                            try:
                                age = float(age_input)
                                if age < 0:
                                    print("Age cannot be negative. Setting to 0.")
                                    age = 0
                                elif age > race_max_age:
                                    print(f"Age cannot exceed {race_max_age} for {race}")
                                    continue
                                break
                            except ValueError:
                                print("Invalid age. Please enter a number.")
                    else:
                        try:
                            age = float(age_str)
                            if age < 0 or age > RACE_STATS[race]['max_age']:
                                print(f"Age {age} is invalid for {race}")
                                continue
                        except ValueError:
                            print("Invalid age in shortcut")
                            continue
                    
                    # Get name
                    while True:
                        name = input("Character name: ").strip()
                        if name:
                            break
                        print("Name cannot be empty. Please try again.")
                    
                    # Validate unlocks
                    if race not in roster.unlocked_races:
                        print(f"Race '{race}' is currently locked.")
                        continue
                    if char_class not in roster.unlocked_classes:
                        print(f"Class '{char_class}' is currently locked.")
                        continue
                    
                    # Add character
                    roster.add_character(name, age, char_class, race, gender)
                    print(f"✓ '{name}' added successfully!")
                    print(f"  Race: {race} | Class: {char_class} | Gender: {gender} | Age: {age}")
                else:
                    # Single or double digit: treat as count
                    count = int(shortcut)
                    if count > 0:
                        add_characters(roster, count)
                    else:
                        print("Invalid count. Must be a positive number.")
            else:
                # parse shortcut for single character
                parts = shortcut.split()
                if len(parts) == 1 and parts[0].isdigit():
                    # Compact index-based shortcut: +2343 (no spaces)
                    indices = list(parts[0])
                    if len(indices) < 3:
                        print("Need at least 3 digits for race, class, gender indices")
                        continue
                    
                    race_idx = int(indices[0])
                    class_idx = int(indices[1])
                    gender_idx = int(indices[2])
                    
                    # Validate indices
                    if not (1 <= race_idx <= len(RACES)):
                        print("Invalid race index")
                        continue
                    if not (1 <= class_idx <= len(CLASSES)):
                        print("Invalid class index")
                        continue
                    if not (1 <= gender_idx <= len(GENDERS)):
                        print("Invalid gender index")
                        continue
                    
                    race = RACES[race_idx - 1]
                    char_class = CLASSES[class_idx - 1]
                    gender_base = GENDERS[gender_idx - 1]
                    
                    sub_idx = int(indices[3]) if len(indices) > 3 else None
                    age_str = ''.join(indices[4:]) if len(indices) > 4 else None
                    name = None
                    
                    if gender_base == 'Trans':
                        subgenders = ['Male', 'Female', 'Non-Binary', 'Other']
                        if sub_idx is not None:
                            if not (1 <= sub_idx <= len(subgenders)):
                                print("Invalid subgender index")
                                continue
                            sub = subgenders[sub_idx - 1]
                            gender = f"Trans ({sub})"
                        else:
                            print("Subgender index required for Trans")
                            continue
                    else:
                        gender = gender_base
                    
                    # Get age if not provided
                    if age_str is None:
                        race_max_age = RACE_STATS[race]['max_age']
                        while True:
                            age_input = input(f"Starting age (years, max {race_max_age}): ").strip()
                            try:
                                age = float(age_input)
                                if age < 0:
                                    print("Age cannot be negative. Setting to 0.")
                                    age = 0
                                elif age > race_max_age:
                                    print(f"Age cannot exceed {race_max_age} for {race}")
                                    continue
                                break
                            except ValueError:
                                print("Invalid age. Please enter a number.")
                    else:
                        try:
                            age = float(age_str)
                            if age < 0 or age > RACE_STATS[race]['max_age']:
                                print(f"Age {age} is invalid for {race}")
                                continue
                        except ValueError:
                            print("Invalid age in shortcut")
                            continue
                    
                    # Get name
                    while True:
                        name = input("Character name: ").strip()
                        if name:
                            break
                        print("Name cannot be empty. Please try again.")
                    
                    # Validate unlocks
                    if race not in roster.unlocked_races:
                        print(f"Race '{race}' is currently locked.")
                        continue
                    if char_class not in roster.unlocked_classes:
                        print(f"Class '{char_class}' is currently locked.")
                        continue
                    
                    # Add character
                    roster.add_character(name, age, char_class, race, gender)
                    print(f"✓ '{name}' added successfully!")
                    print(f"  Race: {race} | Class: {char_class} | Gender: {gender} | Age: {age}")
                elif len(parts) >= 3 and all(p.isdigit() for p in parts):
                    # Spaced index-based shortcut: +2 3 4 2 [age] [name]
                    race_idx = int(parts[0])
                    class_idx = int(parts[1])
                    gender_idx = int(parts[2])
                    
                    # Validate indices
                    if not (1 <= race_idx <= len(RACES)):
                        print("Invalid race index")
                        continue
                    if not (1 <= class_idx <= len(CLASSES)):
                        print("Invalid class index")
                        continue
                    if not (1 <= gender_idx <= len(GENDERS)):
                        print("Invalid gender index")
                        continue
                    
                    race = RACES[race_idx - 1]
                    char_class = CLASSES[class_idx - 1]
                    gender_base = GENDERS[gender_idx - 1]
                    
                    sub_idx = None
                    age_str = None
                    name = None
                    
                    if gender_base == 'Trans':
                        subgenders = ['Male', 'Female', 'Non-Binary', 'Other']
                        if len(parts) > 3:
                            sub_idx = int(parts[3])
                            if not (1 <= sub_idx <= len(subgenders)):
                                print("Invalid subgender index")
                                continue
                            sub = subgenders[sub_idx - 1]
                            gender = f"Trans ({sub})"
                            if len(parts) > 4:
                                age_str = parts[4]
                            if len(parts) > 5:
                                name = parts[5]
                        else:
                            print("Subgender index required for Trans")
                            continue
                    else:
                        gender = gender_base
                        if len(parts) > 3:
                            age_str = parts[3]
                        if len(parts) > 4:
                            name = parts[4]
                    
                    # Get age if not provided
                    if age_str is None:
                        race_max_age = RACE_STATS[race]['max_age']
                        while True:
                            age_input = input(f"Starting age (years, max {race_max_age}): ").strip()
                            try:
                                age = float(age_input)
                                if age < 0:
                                    print("Age cannot be negative. Setting to 0.")
                                    age = 0
                                elif age > race_max_age:
                                    print(f"Age cannot exceed {race_max_age} for {race}")
                                    continue
                                break
                            except ValueError:
                                print("Invalid age. Please enter a number.")
                    else:
                        try:
                            age = float(age_str)
                            if age < 0 or age > RACE_STATS[race]['max_age']:
                                print(f"Age {age} is invalid for {race}")
                                continue
                        except ValueError:
                            print("Invalid age in shortcut")
                            continue
                    
                    # Get name if not provided
                    if name is None:
                        while True:
                            name = input("Character name: ").strip()
                            if name:
                                break
                            print("Name cannot be empty. Please try again.")
                    
                    # Validate unlocks
                    if race not in roster.unlocked_races:
                        print(f"Race '{race}' is currently locked.")
                        continue
                    if char_class not in roster.unlocked_classes:
                        print(f"Class '{char_class}' is currently locked.")
                        continue
                    
                    # Add character
                    roster.add_character(name, age, char_class, race, gender)
                    print(f"✓ '{name}' added successfully!")
                    print(f"  Race: {race} | Class: {char_class} | Gender: {gender} | Age: {age}")
                elif len(parts) == 5:
                    race, char_class, gender, age_str, name = parts
                elif len(parts) == 6:
                    race, char_class, gender1, gender2, age_str, name = parts
                    if gender1 == "Trans":
                        gender = f"Trans ({gender2})"
                    else:
                        print("Invalid gender format. For Trans, use 'Trans subgender'.")
                        continue
                else:
                    print("Invalid shortcut format. Use '+2343' (compact indices), '+2 3 4 2' (spaced indices), '+race class gender age name' (text), or '+race class Trans subgender age name' (Trans text)")
                    continue
                
                if not ( (len(parts) == 1 and parts[0].isdigit()) or (len(parts) >= 3 and all(p.isdigit() for p in parts)) ):  # If not index-based, do the text validation
                    try:
                        age = float(age_str)
                        # validate race
                        if race not in RACE_STATS:
                            print(f"Invalid race: {race}")
                            continue
                        if race not in roster.unlocked_races:
                            print(f"Race '{race}' is currently locked.")
                            continue
                        # validate class
                        if char_class not in CLASS_INFO:
                            print(f"Invalid class: {char_class}")
                            continue
                        if char_class not in roster.unlocked_classes:
                            print(f"Class '{char_class}' is currently locked.")
                            continue
                        # validate age
                        if age < 0 or age > RACE_STATS[race]['max_age']:
                            print(f"Age {age} is invalid for {race} (max age: {RACE_STATS[race]['max_age']})")
                            continue
                        # validate name
                        if not name.strip():
                            print("Name cannot be empty.")
                            continue
                        # add character
                        roster.add_character(name, age, char_class, race, gender)
                        print(f"✓ '{name}' added successfully!")
                        print(f"  Race: {race} | Class: {char_class} | Gender: {gender} | Age: {age}")
                    except ValueError:
                        print("Invalid age. Must be a number.")
        elif choice == "-":
            remove_character(roster)
        elif choice == "p":
            display_player(roster)
        elif choice == "r":
            display_random_player(roster)
        elif choice == "t":
            display_all_characters(roster)
        elif choice == "a":
            advance_time(roster)
        elif choice == "u":
            unlock_content_menu(roster)
        elif choice == "s":
            display_stats_info(roster)
        elif choice == "c":
            roster.display_memorial()
        elif choice == "exit" or choice == "e":
            print("Thank you for using SKooKS Roster Manager")
            print("Have a nice day!\n")
            break
        elif choice.lower() == 'cancel':
            print("Exiting roster manager...")
            break
        else:
            print("Invalid command. Please try again.\n")


# ============================================================================
# MAIN GAME CONTROLLER
# ============================================================================
def main_menu(game_state):
    """Main control hub"""
    # Create a persistent roster instance
    if not hasattr(main_menu, 'roster'):
        main_menu.roster = CharacterRoster()
    
    roster = main_menu.roster
    
    print("\n=== SKOOKS GAME CONTROLLER ===")
    print("Commands:")
    print("  Travel (1/T/travel)")
    print("  Party (P/party) - Select adventuring party")
    print("  Roster (2/R/roster)")
    print("  Settings (3/S/settings)")
    print("  Exit (4/E/exit)")
    print("=============================\n")
    
    # Show current party status
    if game_state.selected_party:
        party_info = game_state.get_party_info(roster)
        print(f"Current Party ({len(party_info)} members):")
        for i, char in enumerate(party_info):
            print(f"  {i+1}. {char['name']} ({char['race']} {char['class']})")
        print()
    
    choice = input("Enter command: ]]").strip().lower()
    
    if choice in ["travel", "1", "t"]:
        if roster.is_empty():
            print("No characters available for travel! Create some characters in the Roster first.")
            return
        elif not game_state.selected_party:
            print("No party selected! Choose your adventuring party first.")
            select_party(roster, game_state)
            if game_state.selected_party:  # Check if party was successfully selected
                print("Opening map...\n")
                map_main(game_state, roster)
        else:
            print("Opening map...\n")
            map_main(game_state, roster)
    elif choice in ["party", "p"]:
        if roster.is_empty():
            print("No characters available! Create some characters in the Roster first.")
        else:
            select_party(roster, game_state)
    elif choice in ["roster", "2", "r"]:
        manage_roster(roster)
    elif choice in ["settings", "3", "s"]:
        print("Settings menu not yet implemented.\n")
    elif choice in ["exit", "4", "e"]:
        print("Thanks for playing!")
        game_state.is_running = False
    else:
        print("Invalid command. Please try again.\n")


def main():
    """Main game loop"""
    global PLAYER_NAME
    game_state = GameState()
    player_input = input("Enter your name, adventurer: ").strip()
    if player_input:
        PLAYER_NAME = player_input
    
    while game_state.is_running:
        main_menu(game_state)


if __name__ == "__main__":
    main()
