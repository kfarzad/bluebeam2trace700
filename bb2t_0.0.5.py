### |<|= =|>| ###

### To be developed
## 1. insert wall names, JG
###

### some settings to consider
split_chr = "_"
speed = 0.01 # 0.1
start_delay = 5 # in seconds

### test ground
test_mode = False
test_file_name = "test_"+ "wd_sch" + ".csv"

### Don't mess around below this line
print("")

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
def countdown(seconds=3, message="in"):
    for s in range(seconds, 0, -1):
            print(f"{message}: {s}s", end="\r")
            time.sleep(1)

### read the settings
base_dir = Path(__file__).parent.resolve()

if not test_mode:
    yaml_file_name = "button_map.yaml"
    yaml_paths = [
        base_dir / yaml_file_name,
        base_dir / "tools" / yaml_file_name,
        base_dir / "settings" / yaml_file_name
    ]
    yaml_path = next((p for p in yaml_paths if p.is_file()), None)

    if yaml_path is None:
        print("button_map.yaml file missing\ngo to tools folder and use create_button_map.py to calibrate your program")
        input("press ENTER to exit the program")
        sys.exit(1)
    else:
        with open(str(yaml_path), "r") as f:
            bm = yaml.safe_load(f)
else:
    yaml_file_name = "button_map_kf.yaml"
    yaml_path = str(base_dir) + "/settings/kf/" + yaml_file_name
    with open(str(yaml_path), "r") as f:
        bm = yaml.safe_load(f)

with open(base_dir / "settings/window_to_wall_ratios.yaml", "r") as f:
    wwr = yaml.safe_load(f)
    use_wwr = wwr["use_wwr"]
    if use_wwr:
        print('using window to wall ratios')
        wwr.pop("use_wwr")
        print(wwr)
        wwr_deg_list = pd.Series(list(wwr.keys())).str.extract(r'wwr\s?(\d{3})', expand=False).dropna().tolist()        # example: print(float(wwr["wwr"+"010"]))
    else:
        del wwr

with open(base_dir / "settings/opening_schedule.yaml", "r") as f:
    opn_sch = yaml.safe_load(f)
    use_win_sch = opn_sch["use_window_schedule"]
    use_door_sch = opn_sch["use_door_schedule"]
    if use_win_sch or use_door_sch:
        use_window_type = opn_sch["use_window_type"]
        use_door_type = opn_sch["use_door_type"]
        correct_win_length = opn_sch["correct_window_length"]
        correct_door_length = opn_sch["correct_door_length"]

        if use_window_type and correct_win_length:
            print("you cannot use both window length correction and window type selection together")
            input("press ENTER to exit the program")
            sys.exit(1)
        if use_door_type and correct_door_length:
            print("you cannot use both door length correction and door type selection together")
            input("press ENTER to exit the program")
            sys.exit(1)

        if correct_win_length:
            print('using window schedule for length correction')
            win_sch = opn_sch["window_schedule"]
            win_sch_heights = [h['H'] for h in win_sch.values()]
            win_sch_widths = [w['W'] for w in win_sch.values()]
        elif use_window_type:
            print('using window schedule for window type')
            win_sch = opn_sch["window_schedule"]
            win_sch = {k.lower(): v for k, v in win_sch.items()}
        
        if correct_door_length:
            print('using door schedule')
            door_sch = opn_sch["door_schedule"]
            door_sch_heights = [h['H'] for h in door_sch.values()]
            door_sch_widths = [w['W'] for w in door_sch.values()]
        elif use_door_type:
            print('using door schedule for door type')
            door_sch = opn_sch["door_schedule"]
            door_sch = {k.lower(): v for k, v in door_sch.items()}
    else:
        correct_win_length = False
        correct_door_length = False

with open(base_dir / "settings/default_values.yaml", "r") as f:
    default_values = yaml.safe_load(f)
    win_def_height = default_values["default_window_height"]
    door_def_height = default_values["default_door_height"]
    # wall_def_orient = default_values["default_wall_orientation"]

### functions
def update_field(input_button, input_text, mod=my_mod, speed=speed, lookup_table=bm):
    print("updating "+ str(input_button) + " -----> "+ str(input_text))
    x, y = lookup_table[input_button]
    input_text = str(input_text)
    if not test_mode:
        pyautogui.click(x=x, y=y, clicks=1, interval=speed)
        time.sleep(speed)
        pyautogui.press('right', presses=15, interval=0.001)
        pyautogui.press('backspace', presses=20, interval=0.001)
        pyautogui.write(input_text, interval=speed)

def click_field(input_button, lookup_table=bm):
    print("clicking "+ str(input_button))
    x, y = lookup_table[input_button]
    if not test_mode:
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

def check_prohibited_chars(names, prohibited_list):
    invalid_items = []
    
    for name in names:
        found = [c for c in prohibited_list if re.search(re.escape(c), name)]

        if found:
            invalid_items.append((name, ", ".join(found)))

    if invalid_items:
        print("CRITICAL ERROR — names contain prohibited characters:")
        
        for item, bad_chars in invalid_items:
            print(f"(Illegal: {bad_chars})  {item}")

        input("\nPress ENTER to exit the program")
        sys.exit(1)

def check_smaller_than_1_1(measurement, multiplier=1):
    invalid_items = []

    for i in range(len(measurement)):
        rm_size = round(measurement.at[i, 'Measurement']/multiplier,2)

        if rm_size < 1.1:
            name = measurement.at[i, 'Label']
            invalid_items.append((name, rm_size))

    if invalid_items:
        print("CRITICAL ERROR — Measurement is smaller than threshold:\n")

        for item, value in invalid_items:
            print(f"{item}: {value*multiplier} < {1.1*multiplier}")

        input("\nPress ENTER to exit the program")
        sys.exit(1)

### starting the code
if not test_mode:
    countdown(start_delay, "Starting in")

start_time = time.perf_counter()

if not test_mode:
    input_file = list(base_dir.glob("*.csv"))
else:
    input_file = [str(base_dir) + "/test/" + test_file_name]

if len(input_file) == 1:
    target_csv = input_file[0]
else:
    print(f"CRITICAL ERROR - expected 1 csv, but found {len(input_file)}.")
    input("press ENTER to exit the program")
    sys.exit(1)

df = pd.read_csv(str(input_file[0]))

cols = df.columns.str.strip()
if not 'Label' in cols:
    if 'Subject' in cols:
        df['Label'] = df['Subject']
    else:
        print(f"CRITICAL ERROR - input file does NOT have a Label or Subject column.")
        input("press ENTER to exit the program")
        sys.exit(1)
elif 'Label' in cols and 'Subject' in cols:
        print(f"CRITICAL ERROR - input file has both Label and Subject columns, please remove one.")
        input("press ENTER to exit the program")
        sys.exit(1) 

df = df.dropna(subset=['Label'])
df = df[~df['Label'].str.contains('guide', case=False, na=False)]
df = df.reset_index(drop=True)
df = df.sort_values(by=["Label"],ascending=[True])
df['Label_Original'] = df['Label']  # Save for Trace700
df['Label'] = df['Label'].str.lower() # Lowercase for logic
df = round(df,1)

if not 'Measurement' in cols:
    if 'Area' in cols and 'Length' not in cols and 'Count' not in cols:
        df['Measurement'] = df['Area']
        if 'Area Unit' in cols:
            df['Measurement Unit'] = df['Area Unit']
    elif 'Length' in cols and 'Area' not in cols and 'Count' not in cols:
        df['Measurement'] = df['Length']
        if 'Length Unit' in cols:
            df['Measurement Unit'] = df['Length Unit']
    elif 'Count' in cols and 'Area' not in cols and 'Length' not in cols:
        df['Measurement'] = df['Count']
        if 'Count Unit' in cols:
            df['Measurement Unit'] = df['Count Unit']  
    else:
        print(f"CRITICAL ERROR - input file has at least two of the following Area/Length/Count without Measurement columns,\nplease include Measurement column!")
        input("press ENTER to exit the program")
        sys.exit(1)

rooms = df
rooms = rooms[~rooms['Label'].str.split(split_chr).str[1:].str.join(split_chr).str.contains('pop|wall|window|win|zone', case=False, na=False)]
rooms = rooms.reset_index(drop=True)
n_rooms = len(rooms)
check_long_names(rooms['Label'])
check_prohibited_chars(rooms['Label'], [".", ";", "\\", "'", '"'])
check_smaller_than_1_1(rooms,10)

walls = df
walls = walls[walls['Label'].str.split(split_chr).str[1:].str.join(split_chr).str.contains('wall', case=False, na=False)]
walls = walls.reset_index(drop=True)
walls_extracted = walls['Label'].str.extract(r'(_\s*wall.*?\d{3}\s*_?)', expand=False, flags=re.IGNORECASE)
if walls_extracted.isna().any():
    invalid_rows = walls[walls_extracted.isna()]['Label'].tolist()
    print(f"CRITICAL ERROR")
    for item in invalid_rows:
        print(f"{item} is missing or wrong orientation")
    input("press ENTER to exit the program")
    sys.exit(1)
check_smaller_than_1_1(walls, 1)

if use_win_sch:
    if use_window_type:
        wtypes = df
        wtypes = wtypes[wtypes['Label'].str.split(split_chr).str[1:].str.join(split_chr).str.contains('wtype', case=False, na=False)]
        wtypes = wtypes.reset_index(drop=True)
        wtypes_extracted = wtypes['Label'].str.extract(r"wtype\s*(\S+)\s*", expand=False, flags=re.IGNORECASE)
        wtypes_extracted = wtypes_extracted.dropna().unique().tolist()
        invalid_items = []
        for wtype in wtypes_extracted:
            if wtype.lower() not in win_sch.keys():
                invalid_items.append(wtype)
        if invalid_items:
            print("CRITICAL ERROR — window schedule missing:")
            for item in invalid_items:
                print(f"Not in schedule:  {item}")
            input("\nPress ENTER to exit the program")
            sys.exit(1)

if use_door_sch:
    if use_door_type:
        dtypes = df
        dtypes = dtypes[dtypes['Label'].str.split(split_chr).str[1:].str.join(split_chr).str.contains('dtype', case=False, na=False)]
        dtypes = dtypes.reset_index(drop=True)
        dtypes_extracted = dtypes['Label'].str.extract(r"dtype\s*(\S+)\s*", expand=False, flags=re.IGNORECASE)
        dtypes_extracted = dtypes_extracted.dropna().unique().tolist()
        invalid_items = []
        for dtype in dtypes_extracted:
            if dtype.lower() not in door_sch.keys():
                invalid_items.append(dtype)
        if invalid_items:
            print("CRITICAL ERROR — door schedule missing:")
            for item in invalid_items:
                print(f"Not in schedule:  {item}")
            input("\nPress ENTER to exit the program")
            sys.exit(1)

if use_wwr:
    walls_extracted_digits = walls['Label'].str.extract(r'_?\s*wall.*?(\d{3})\s*_?', expand=False, flags=re.IGNORECASE)
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

click_field("trace_logo_on_program_title_bar")
click_field("create_rooms_house_icon")

for i in range(0, len(rooms)):
    print("")
    print("--- new room ---")
    print("")
    click_field("single_sheet_tab_button")
    click_field("single_sheet_new_room_button")

    print("")
    print(rooms.at[i,'Label_Original'])
    print("")
    update_field("single_sheet_room_description_inputfield", rooms.at[i,'Label_Original'])

    room_length = round(rooms.at[i,'Measurement']/10,2)
    update_field("single_sheet_floor_length_inputfield", room_length)

    room_num = re.search(r"\s+x(\d+)", rooms.at[i,'Label'].split(split_chr)[0])
    if room_num != None:
        room_num = int(room_num.group(1))
        click_field("rooms_tab_button")
        update_field("rooms_duplicate_rooms_per_zone_inputfield", room_num)
    print("")

    ### get details of the room
    base_label = re.escape(str(rooms.at[i, 'Label']))
    suffix_sep = re.escape(split_chr)
    search_pattern = fr"^{base_label}\s*(?:{suffix_sep}|$)"
    tdf = df[df["Label"].str.contains(search_pattern, regex=True, na=False)]
    tdf = tdf.reset_index(drop=True)

    if len(tdf)>1:
        for ii in range(1, len(tdf)): # skips the name part and starts from second string
            label = tdf.at[ii,'Label']
            print(label)
            label_parts = label.split(split_chr)

            ### pop
            if 'pop' in label:
                room_pop = tdf.at[ii,'Measurement']

                click_field("single_sheet_tab_button")
                click_field("single_sheet_internal_loads_people_dropdown_arrow")
                click_field("single_sheet_internal_loads_people_dropdown_people")
                update_field("single_sheet_internal_loads_people_inputfield", room_pop)

                room_pop = None

            ### wall
            if 'wall' in label and not any(x in label for x in ('win', 'window', 'wtype', 'door', 'dtype')):
                click_field("walls_tab_button")
                click_field("walls_new_wall_button")
                wall_length = tdf.at[ii,'Measurement']

                for iii, p in enumerate(label_parts):
                    if 'wall' in p:
                        s = p.replace(" ", "")
                        wall_direction = int(re.search(r'_?\s*wall.*?(\d{3})\s*_?', s.lower()).group(1))
                        update_field("walls_wall_direction_inputfield", wall_direction)

                update_field("walls_wall_length_inputfield", wall_length)

                if use_wwr:
                    click_field("walls_new_opening_button")
                    click_field("walls_openings_window_checkbox")
                    click_field("walls_openings_wall_area_checkbox")
                    update_field("walls_openings_wall_area_inputfield", round(float(wwr["wwr"+f"{wall_direction:03d}"]) * 100, ndigits= 2))

                iii = wall_length = p = s = wall_direction = wall_length = None

            ### single windows
            if not use_wwr:
                if any(x in label for x in ('win', 'window', 'wtype')):
                    click_field("walls_new_opening_button")
                    click_field("walls_openings_window_checkbox")
                    click_field("walls_openings_length_checkbox")

                    for iii, p in enumerate(label_parts):
                        if any(x in p for x in ('win', 'window')):
                            win_height = re.search(r"h(\d+(?:\.\d+)?)", p)

                            if win_height == None:
                                win_height = win_def_height
                                collector.collect(f"using default window height value ({win_def_height}) for: {label}")
                            else:
                                win_height = float(win_height.group(1))

                            win_num = re.search(r"\s+x(\d+)", p)
                            if win_num != None:
                                win_num = int(win_num.group(1))
                                update_field("walls_openings_quantity_inputfield", win_num)

                            win_length = tdf.at[ii,'Measurement']

                            if correct_win_length:
                                win_length = min(win_sch_widths, key=lambda x: abs(x - win_length))

                        elif 'wtype' in p:
                            win_type = str(re.search(r"wtype\s*(\S+)\s*", p).group(1))
                            win_height = win_sch[win_type]['H']
                            win_length = win_sch[win_type]['W']
                            
                            win_num = re.search(r"\s+x(\d+)", p)
                            if win_num != None:
                                win_num = int(win_num.group(1))
                                update_field("walls_openings_quantity_inputfield", win_num)

                    update_field("walls_openings_height_inputfield", win_height)
                    update_field("walls_openings_length_inputfield", win_length)

                    iii = p = win_height = win_num = win_length = win_type = None

            ### door
            if any(x in label for x in ('door', 'dtype')):
                click_field("walls_new_opening_button")
                click_field("walls_openings_door_checkbox")
                click_field("walls_openings_length_checkbox")

                for iii, p in enumerate(label_parts):
                    if 'door' in p:
                        door_height = re.search(r"h(\d+(?:\.\d+)?)", p)

                        if door_height == None:
                            door_height = door_def_height
                            collector.collect(f"using default door height value ({door_def_height}) for: {label}")
                        else:
                            door_height = float(door_height.group(1))

                        door_num = re.search(r"\s+x(\d+)", p)
                        if door_num != None:
                            door_num = int(door_num.group(1))
                            update_field("walls_openings_quantity_inputfield", door_num)

                        door_length = tdf.at[ii,'Measurement']

                        if correct_door_length:
                            door_length = min(door_sch_widths, key=lambda x: abs(x - door_length))

                    elif 'dtype' in p:
                        door_type = str(re.search(r"dtype\s*(\S+)\s*", p).group(1))
                        door_height = door_sch[door_type]['H']
                        door_length = door_sch[door_type]['W']
                        
                        door_num = re.search(r"\s+x(\d+)", p)
                        if door_num != None:
                            door_num = int(door_num.group(1))
                            update_field("walls_openings_quantity_inputfield", door_num)

                update_field("walls_openings_length_inputfield", door_length)
                update_field("walls_openings_height_inputfield", door_height)

                iii = p = door_height = door_num = door_length = door_type = None
            print("")
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
if not test_mode:
    input("press ENTER 3 times to exit the program")
    input("press ENTER 2 times to exit the program")
    input("press ENTER 1 time to exit the program")
print("|<|= =|>|")
time.sleep(1)

