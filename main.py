### by Kiarash Farzad

split_chr = "_"
speed = 0.05 #0.1


import sys
from pathlib import Path
import time
import re
import platform
from datetime import timedelta

import yaml
import pyautogui
import pandas as pd

### read the settings
with open("button_map.yaml", "r") as f:
    bm = yaml.safe_load(f)

with open("wwr.yaml", "r") as f:
    wwr = yaml.safe_load(f)
    use_wwr = wwr["use_wwr"]
    if use_wwr:
        print('using wwr')
        wwr.pop("use_wwr")
        print(wwr)
        #example
        # print(float(wwr["wwr"+"010"]))
    else:
        del wwr


### starting the code
for i in range(5, 0, -1):
        print(f"Starting in: {i}...", end="\r")
        time.sleep(1)

start_time = time.perf_counter()

my_mod = 'command' if platform.system() == 'Darwin' else 'ctrl'
def update_field(input_button, input_text, mod=my_mod, speed=speed, lookup_table=bm):
    print("updating "+ str(input_button) + " to "+ str(input_text))
    x, y = lookup_table[input_button]
    input_text = str(input_text)

    pyautogui.click(x=x, y=y, clicks=1, interval=speed)
    time.sleep(speed)

    # pyautogui.hotkey(mod, 'a')
    # pyautogui.press('backspace')
    pyautogui.press('right', presses=15, interval=0.001)
    # pyautogui.press('backspace', presses=20, interval=0.001)

    pyautogui.write(input_text, interval=speed)
    pyautogui.press('return')

def click_field(input_button, lookup_table=bm):
    print("clicking "+ str(input_button))
    x, y = lookup_table[input_button]
    pyautogui.click(x=x, y=y, clicks=1, interval=speed)
    time.sleep(speed)

script_dir = Path(__file__).parent.absolute()
input_file = list(script_dir.glob("*.csv"))

if len(input_file) == 1:
    target_csv = input_file[0]
    print(f"File found: {target_csv.name}")
else:
    print(f"CRITICAL ERROR: Expected 1 CSV, but found {len(input_file)}.")
    print("Program exiting...")
    sys.exit(1)

df = pd.read_csv(str(input_file[0]))
df = df.dropna(subset=['Label'])
df = df[~df['Label'].str.contains('guide', case=False, na=False)]
df = df.reset_index(drop=True)
df = df.sort_values(by=["Label","Count"],ascending=[True, True])
df = round(df,1)

rooms = df
rooms = rooms[~rooms['Label'].str.contains('pop|wall|window', case=False, na=False)]
rooms = rooms[~rooms['Measurement Unit'].str.contains('count', case=False, na=False)]
rooms = rooms.reset_index(drop=True)
n_rooms = len(rooms)

for i in range(0, len(rooms)):
    print(" ")
    click_field("single_sheet_tab_button")
    click_field("single_sheet_new_room_button")

    print(rooms.at[i,'Label'])
    update_field("single_sheet_room_description_inputfield", rooms.at[i,'Label'])

    room_length = round(rooms.at[i,'Measurement']/10,2)
    print('room length/10: ' + str(room_length))
    update_field("single_sheet_floor_length_inputfield", room_length)

    room_num = re.search(r"x(\d+)", rooms.at[i,'Label'].split(split_chr)[0])
    if room_num != None:
        room_num = int(room_num.group(1))
        print('room num: ' + str(room_num))
        click_field("rooms_tab_button")
        update_field("rooms_duplicate_rooms_per_zone_inputfield", room_num)

    # get details of the room
    tdf = df[df["Label"].str.contains(rooms.at[i,'Label'], na=False)]
    tdf = tdf.reset_index(drop=True)

    if len(tdf)>1:
        for ii in range(1, len(tdf)):
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
                    update_field("walls_openings_wall_area_inputfield", float(wwr["wwr"+f"{wall_direction:03d}"]) * 100)

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
                            win_height = int(win_height.group(1))
                            print('win height: ' + str(win_height))
                            update_field("walls_openings_height_inputfield", win_height)
                            win_num = re.search(r"x(\d+)", p)
                            if win_num != None:
                                win_num = int(win_num.group(1))
                                print('win num: ' + str(win_num))
                                update_field("walls_openings_quantity_inputfield", win_num)
                    win_length = tdf.at[ii,'Measurement']
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
                        door_height = int(door_height.group(1))
                        print('door height: ' + str(door_height))
                        update_field("walls_openings_height_inputfield", door_height)
                        door_num = re.search(r"x(\d+)", p)
                        if door_num != None:
                            door_num = int(door_num.group(1))
                            print('door num: ' + str(door_num))
                            update_field("walls_openings_quantity_inputfield", door_num)
                door_length = tdf.at[ii,'Measurement']
                print('door length: ' + str(door_length))
                update_field("walls_openings_length_inputfield", door_length)

                iii = p = door_height = door_num = door_length = None

    tdf = None

total_seconds = time.perf_counter() - start_time
print(f"Total execution time: {timedelta(seconds=total_seconds)}")
