import yaml
from pynput import mouse

# 2. Define the topics to locate
topics = [
"trace_logo_on_program_title_bar",
"create_rooms_house_icon",
"single_sheet_tab_button",
"single_sheet_new_room_button",
"single_sheet_room_description_inputfield",
"single_sheet_floor_length_inputfield",
"single_sheet_floor_width_inputfield",
"single_sheet_internal_loads_people_inputfield",
"single_sheet_internal_loads_people_dropdown_arrow",
"single_sheet_internal_loads_people_dropdown_people",
"rooms_tab_button",
"rooms_duplicate_rooms_per_zone_inputfield",
"walls_tab_button",
"walls_new_wall_button",
"walls_wall_length_inputfield",
"walls_wall_direction_inputfield",
"walls_new_opening_button",
"walls_openings_window_checkbox",
"walls_openings_door_checkbox",
"walls_openings_wall_area_checkbox",
"walls_openings_wall_area_inputfield",
"walls_openings_length_checkbox",
"walls_openings_length_inputfield",
"walls_openings_height_inputfield",
"walls_openings_quantity_inputfield"
]

results = {}
current_index = 0

print("")
print("")
print("")
print("--- UI COORDINATE CAPTURE TOOL ---")
print("")
print(f"Next Target: {topics[current_index]}")

def on_click(x, y, button, pressed):
    global current_index
    if pressed:
        label = topics[current_index]
        results[label] = [int(x), int(y)]
        print(f"Captured {label}: [{int(x)}, {int(y)}]")
        print("")
        
        current_index += 1
        
        if current_index < len(topics):
            print(f"Next Target: {topics[current_index]}")
        else:
            print("All coordinates captured!")
            return False # Stops the listener

# 3. Start Listening
with mouse.Listener(on_click=on_click) as listener:
    listener.join()

# 4. Save to YAML
with open("button_map.yaml", "w") as f:
    yaml.dump(results, f, sort_keys=False)

print("File 'button_map.yaml' has been created successfully.")
input("press ENTER to exit the program")