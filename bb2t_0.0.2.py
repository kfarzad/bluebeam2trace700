### |<|= =|>| ###

split_chr = "_"
speed = 0.1 #0.1

### Don't mess around below this line
import sys
from pathlib import Path
import time
import re
import platform
from datetime import timedelta

import yaml
import pyautogui
import pandas as pd

class WarningCollector:
    def __init__(self):
        self.warnings = []

    def collect(self, message, row_index=None):
        """Adds a warning to the list with optional row context."""
        prefix = f"Row {row_index}: " if row_index is not None else ""
        self.warnings.append(f"{prefix}{message}")

    def display_summary(self):
        """Prints a clean report at the end of the execution."""
        print("\n" + "="*30)
        print("="*10 + " WARNINGS " + "="*10)
        print("="*30)
        
        if not self.warnings:
            print("✅ No warnings.")
        else:
            print(f"⚠️ Found {len(self.warnings)} warning(s):")
            for warn in self.warnings:
                print(f" - {warn}")
        print("="*30 + "\n")
collector = WarningCollector()

my_mod = 'command' if platform.system() == 'Darwin' else 'ctrl'

### functions
def countdown(seconds=5, message="in"):
    for s in range(seconds, 0, -1):
            print(f"{message}: {s}s", end="\r")
            time.sleep(1)

### read the settings
yaml_file_name = "button_map.yaml"
yaml_paths = [
    Path(".") / yaml_file_name,
    Path("./tools") / yaml_file_name
]
yaml_path = next((p for p in yaml_paths if p.is_file()), None)

if yaml_path is None:
    print("button_map.yaml file missing\ngo to tools folder and use create_button_map.py to calibrate your program")
    input("press ENTER to exit the program")
    countdown(5, "program exiting in")
    sys.exit(1)
else:
    with open(str(yaml_path), "r") as f:
        bm = yaml.safe_load(f)

with open("window_to_wall_ratios.yaml", "r") as f:
    wwr = yaml.safe_load(f)
    use_wwr = wwr["use_wwr"]
    if use_wwr:
        print('using window to wall ratios')
        wwr.pop("use_wwr")
        print(wwr)
        wwr_deg_list = pd.Series(list(wwr.keys())).str.extract(r'wwr\s?(\d{3})', expand=False).dropna().tolist()        # example: print(float(wwr["wwr"+"010"]))
    else:
        del wwr

with open("opening_schedule.yaml", "r") as f:
    opn_sch = yaml.safe_load(f)
    use_opn_sch = opn_sch["use_opening_schedule"]
    if use_opn_sch:
        correct_win_length = opn_sch["correct_window_length"]
        if correct_win_length:
            print('using window schedule')
            window_schedule = opn_sch["win_sch"]
            
            win_sch_heights = [h['H'] for h in window_schedule.values()]
            win_sch_widths = [w['W'] for w in window_schedule.values()]

        correct_door_length = opn_sch["correct_door_length"]
        if correct_door_length:
            print('using door schedule')
            door_schedule = opn_sch["door_sch"]
            
            door_sch_heights = [h['H'] for h in door_schedule.values()]
            door_sch_widths = [w['W'] for w in door_schedule.values()]

    else:
        correct_win_length = False
        correct_door_length = False
        win_def_height = opn_sch["default_window_height"]
        door_def_height = opn_sch["default_door_height"]

### functions
def update_field(input_button, input_text, mod=my_mod, speed=speed, lookup_table=bm):
    print("updating "+ str(input_button) + " to "+ str(input_text))
    x, y = lookup_table[input_button]
    input_text = str(input_text)

    pyautogui.click(x=x, y=y, clicks=1, interval=speed)
    time.sleep(speed)

    pyautogui.press('right', presses=15, interval=0.001)
    pyautogui.press('backspace', presses=20, interval=0.001)

    pyautogui.write(input_text, interval=speed)
    # pyautogui.press('return')

def click_field(input_button, lookup_table=bm):
    print("clicking "+ str(input_button))
    x, y = lookup_table[input_button]
    pyautogui.click(x=x, y=y, clicks=1, interval=speed)
    time.sleep(speed)

def check_long_names(names, limit=40):
    long_items = [n for n in names if len(n) > limit]

    if long_items:
        print("CRITICAL ERROR — names exceed allowed length:")

        for item in long_items:
            print(f"({len(item):>3} chars)  {item}")

        input("press ENTER to exit the program")
        sys.exit(1)

### starting the code
countdown(5, "Starting in")
start_time = time.perf_counter()

script_dir = Path(__file__).parent.absolute()
input_file = list(script_dir.glob("*.csv"))

if len(input_file) == 1:
    target_csv = input_file[0]
    print(f"File found: {target_csv.name}")
else:
    print(f"CRITICAL ERROR - expected 1 csv, but found {len(input_file)}.")
    input("press ENTER to exit the program")
    countdown(5, "program exiting in")
    sys.exit(1)

df = pd.read_csv(str(input_file[0]))
df = df.dropna(subset=['Label'])
df = df[~df['Label'].str.contains('guide', case=False, na=False)]
df = df.reset_index(drop=True)
df = df.sort_values(by=["Label","Count"],ascending=[True, True])
df['Label_Original'] = df['Label']  # Save for Trace700
df['Label'] = df['Label'].str.lower() # Lowercase for logic
df = round(df,1)

rooms = df
# rooms = rooms[~rooms['Label'].str.contains('pop|wall|window', case=False, na=False)]
rooms = rooms[~rooms['Label'].str.split(split_chr).str[1:].str.join(split_chr).str.contains('pop|wall|window|win|zone', case=False, na=False)]
rooms = rooms[~rooms['Measurement Unit'].str.contains('count', case=False, na=False)]
rooms = rooms.reset_index(drop=True)
n_rooms = len(rooms)
check_long_names(rooms['Label'])

walls = df
walls = walls[walls['Label'].str.split(split_chr).str[1:].str.join(split_chr).str.contains('wall', case=False, na=False)]
walls_extracted = walls['Label'].str.extract(r'(wall\s?\d{3})', expand=False, flags=re.IGNORECASE)
if walls_extracted.isna().any():
    invalid_rows = walls[walls_extracted.isna()]['Label'].tolist()
    print(f"CRITICAL ERROR")
    for item in invalid_rows:
        print(f"{item} is missing or wrong orientation")
    input("press ENTER to exit the program")
    sys.exit(1)

if use_wwr:
    walls_extracted_digits = walls['Label'].str.extract(r'wall\s?(\d{3})', expand=False, flags=re.IGNORECASE)
    invalid_rows=walls[~walls_extracted_digits.isin(wwr_deg_list)]
    if not len(invalid_rows) == 0:
        print(f"CRITICAL ERROR")
        for item in invalid_rows['Label']:
            print(f"{item} is missing wwr orientation definition")
        input("press ENTER to exit the program")
        sys.exit(1)

print("")
print("")
print("")

click_field("trace_program_logo")
click_field("create_rooms")

for i in range(0, len(rooms)):
    print("")
    click_field("single_sheet_tab_button")
    click_field("single_sheet_new_room_button")

    print(rooms.at[i,'Label_Original'])
    update_field("single_sheet_room_description_inputfield", rooms.at[i,'Label_Original'])

    room_length = round(rooms.at[i,'Measurement']/10,2)
    print('room length/10: ' + str(room_length))
    update_field("single_sheet_floor_length_inputfield", room_length)

    room_num = re.search(r"\s+x(\d+)", rooms.at[i,'Label'].split(split_chr)[0])
    if room_num != None:
        room_num = int(room_num.group(1))
        print('room num: ' + str(room_num))
        click_field("rooms_tab_button")
        update_field("rooms_duplicate_rooms_per_zone_inputfield", room_num)

    # get details of the room
    search_pattern = r'^' + re.escape(str(rooms.at[i,'Label'])) + r'\s*(' + re.escape(split_chr) + r'|$)'
    tdf = df[df["Label"].str.contains(search_pattern, regex=True, na=False)]
    # tdf = df[df["Label"].str.contains(rooms.at[i,'Label'], na=False)]
    tdf = tdf.reset_index(drop=True)

    if len(tdf)>1:
        for ii in range(1, len(tdf)): # skips the name part and starts from second string
            label = tdf.at[ii,'Label']
            print(label)
            label_parts = label.split(split_chr)

            #pop
            if 'pop' in label:
                room_pop = tdf.at[ii,'Count']
                print('people: ' + str(room_pop))
                click_field("single_sheet_tab_button")
                click_field("single_sheet_internal_loads_people_dropdown_arrow")
                click_field("single_sheet_internal_loads_people_dropdown_people")
                update_field("single_sheet_internal_loads_people_inputfield", room_pop)

                room_pop = None

            #wall
            if 'wall' in label and not any(x in label for x in ('win', 'window', 'door')):
                click_field("walls_tab_button")
                click_field("walls_new_wall_button")
                wall_length = tdf.at[ii,'Measurement']
                for iii, p in enumerate(label_parts):
                    if 'wall' in p:
                        s = p.replace(" ", "")
                        wall_direction = int(s.lower()[-3:])
                        print('wall direction: ' + str(wall_direction))
                        update_field("walls_wall_direction_inputfield", wall_direction)
                print('wall length: ' + str(wall_length))
                update_field("walls_wall_length_inputfield", wall_length)

                if use_wwr:
                    click_field("walls_new_opening_button")
                    click_field("walls_openings_window_checkbox")
                    click_field("walls_openings_wall_area_checkbox")
                    update_field("walls_openings_wall_area_inputfield", round(float(wwr["wwr"+f"{wall_direction:03d}"]) * 100, ndigits= 2))

                iii = wall_length = p = s = wall_direction = wall_length = None

            # single windows
            if not use_wwr:
                if any(x in label for x in ('win', 'window')):
                    click_field("walls_new_opening_button")
                    click_field("walls_openings_window_checkbox")
                    click_field("walls_openings_length_checkbox")
                    for iii, p in enumerate(label_parts):
                        if any(x in p for x in ('win', 'window')):
                            win_height = re.search(r"h(\d+)", p)
                            if win_height == None:
                                win_height = win_def_height
                                collector.collect("using default window height value for: " + str(label))
                            else:
                                win_height = int(win_height.group(1))
                            print('win height: ' + str(win_height))
                            update_field("walls_openings_height_inputfield", win_height)
                            win_num = re.search(r"\s+x(\d+)", p)
                            if win_num != None:
                                win_num = int(win_num.group(1))
                                print('win num: ' + str(win_num))
                                update_field("walls_openings_quantity_inputfield", win_num)
                    win_length = tdf.at[ii,'Measurement']
                    if correct_win_length:
                        win_length = min(win_sch_widths, key=lambda x: abs(x - win_length))
                    print('win length: ' + str(win_length))
                    update_field("walls_openings_length_inputfield", win_length)

                    iii = p = win_height = win_num = win_length = None

            #door
            if 'door' in label:
                click_field("walls_new_opening_button")
                click_field("walls_openings_door_checkbox")
                click_field("walls_openings_length_checkbox")
                for iii, p in enumerate(label_parts):
                    if 'door' in p:
                        door_height = re.search(r"h(\d+)", p)
                        if door_height == None:
                            door_height = door_def_height
                            collector.collect("using default door height value for: " + str(label))
                        else:
                            door_height = int(door_height.group(1))
                        print('door height: ' + str(door_height))
                        update_field("walls_openings_height_inputfield", door_height)
                        door_num = re.search(r"\s+x(\d+)", p)
                        if door_num != None:
                            door_num = int(door_num.group(1))
                            print('door num: ' + str(door_num))
                            update_field("walls_openings_quantity_inputfield", door_num)
                door_length = tdf.at[ii,'Measurement']
                if correct_door_length:
                    door_length = min(door_sch_widths, key=lambda x: abs(x - door_length))
                print('door length: ' + str(door_length))
                update_field("walls_openings_length_inputfield", door_length)

                iii = p = door_height = door_num = door_length = None

    tdf = None

print("")
print("")
print("")
print("="*30)
total_seconds = time.perf_counter() - start_time
print(f"Total execution time: {timedelta(seconds=int(total_seconds))}")
print("="*30)
print("")
collector.display_summary()
input("press ENTER to exit the program")
print("|<|= =|>|")
time.sleep(1)

