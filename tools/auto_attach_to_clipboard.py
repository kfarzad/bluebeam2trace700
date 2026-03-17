import pyperclip
import time

attach_string = input("What do you want to the end of your clipboard (write the word and press Enter)? ")
attach_string = "_" + attach_string
print("Now start using it, and once you are done just click X to exit.")
last_text = ""

while True:
    text = pyperclip.paste()

    # new clipboard content detected
    if text != last_text and text.strip() != "":
        modified = text + attach_string
        pyperclip.copy(modified)
        last_text = modified  # prevent infinite self-trigger
    else:
        last_text = text

    time.sleep(0.15)