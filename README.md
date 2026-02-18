# BlueBeam to Trace700 Automation

Hi! Welcome to the **BlueBeam to Trace700** automation tool. This script is designed to streamline your workflow by automating data entry from BlueBeam CSV outputs directly into Trace 700.

---

## 1. Installation and Calibration

*Complete these steps once. If you have already configured the tool, skip to Step 2.*

### 1.1 Python Installation

1. Go to the **installation folder**.
2. Install Python.
3. Run `install_libraries.py`.

### 1.2 Calibrate Mouse Locations

This step allows the script to "see" where buttons are located in Trace 700.

1. Go to the **tools folder**.
2. Open your **Trace 700** program and navigate to **Create Rooms**.
3. **Position your window:** Drag and set your Trace program anywhere on your screen.
   * *Tip for Windows 11:* I suggest snapping the Trace window to the far right side of your screen.
   * **Important:** This position must remain the same for all future runs and should NOT be covered by other programs.
4. Run `create_button_map.py`.
5. The program will ask you to click on different buttons in Trace 700 to calibrate.
   * *Note: If you click the wrong spot, simply re-run the script.*

---

## 2. Prepare Data

Drop your **BlueBeam output (CSV file)** into the project folder.

## 3. Run Automation

Run the main script: `bb2t_x.x.x.py`.

## 4. Finish

Enjoy and sip your coffee while the automation handles the work! ☕

---

## 5. Naming Scheme

To ensure the script parses your data correctly, follow this naming convention for your BlueBeam markup labels. You can also refer to the **`test.csv`** file under the **`example`** folder for live examples.

### **Either room number or room name or both** (Mandatory)

* *Restriction: No "_" usage within this part.*
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
  * **Manual:** Adjust size (matching the closest window schedule) and quantity.
  * **WWR:** Automate based on Window-to-Wall Ratios using `window_to_wall_ratios.yaml` settings.
* **Doors**
  * Adjust door sizes and quantities.

> **Try the Test File:** There is a sample file located in the `test` folder if you want to give it a try!
