# BlueBeam to Trace700 Automation

Hi! Welcome to the BlueBeam to Trace700 automation tool. This script is designed to streamline your workflow by automating data entry from BlueBeam CSV outputs directly into Trace 700.

---

## 1. Get Started

*Complete steps 1.1 and 1.2 once.
If you have already completed Step 1, skip to Step 2.*

### 1.1 Python Installation

1. Go to the **installation folder**.
2. Install Python.
3. Run `install_libraries.py`.

### 1.2 Mouse Calibration

This step allows the script to "see" where buttons are located in Trace 700.

1. Open your Trace 700 program and navigate to Create Rooms.
2. Drag and set your Trace program anywhere on your screen.
   * *Tip for Windows 11:* I suggest snapping the Trace window to the far right side of your screen.
   * **This position must remain the same for all future runs and should NOT be covered by any other programs.**
3. Go to the tools folder.
4. When you run `create_button_map.py` program, it will ask you to click on different buttons in Trace 700 to calibrate.
   * ***Do not click anywhere else except the button that is asked for!***
   * ***If Trace throws error, skip the error by hitting Enter, and NOT clicking!***
   * ***Do not double-click!***
   * ***Do not move python window!***
   * *If you click the wrong spot, simply re-run the script.*
5. Now run `create_button_map.py`.
   * *You may need to try it few times to get the hang of it.*

---

## 2. Prepare Data

Drop your **BlueBeam output (CSV file)** into the project folder.

* *The BlueBeam output must include "Label" column*
* *For further notes on what to include in Label check Naming Scheme down below*

## 3. Run Automation

Run the main script: `bb2t_x.x.x.py`.

## 4. Finish

Enjoy and sip your coffee while the automation handles the work! ☕

---

## Naming Scheme

To ensure the script parses your data correctly, follow this naming convention for your BlueBeam markup labels. You can also refer to the `b` file under the `b` folder for live examples.

### **Either room number or room name or both** (Mandatory)

* ***Restriction: No "_" usage within this part.***
* *Optional: You can add a multiplier here, example: `101 Office x2`*

--- From here on, any addition is optional ---

### **_wall 135**

* *For wall definitions, the 3 digits represent the orientation of the wall.*
* *Example: `101 Office x2_wall 135`*

### **_window or door h8 x3**

* *For window or door definition: **h** is for height and **x** represents the multiplier.*
* *Note: This should follow a wall definition.*
* *Example: `101 Office x2_wall 135_window h8 x3`*

---

## Features & Capabilities

Looking for more? This program can automate the following:

* **Rooms**
  * Create rooms and adjust sizes.
  * Adjust room multipliers (e.g., x3).
* **Population**
  * Add # of people to the room.
* **Walls**
  * Adjust wall lengths and orientations.
* **Windows**
  * **Manual:** Adjust quantity and size (matching the closest window size, use `settings/opening_schedule.yaml`).
  * **WWR:** Automate based on Window-to-Wall Ratios using `settings/window_to_wall_ratios.yaml` settings.
* **Doors**
  * Adjust quantity and size (matching the closest door size, use `settings/opening_schedule.yaml`).

> **Try the Test File:** There is a sample file located in the `test` folder if you want to give it a try!
