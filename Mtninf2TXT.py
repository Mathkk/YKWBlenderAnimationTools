import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox

# Constantes
FRAME_START = 0x4C
FRAME_END = 0x50
ACTION = 0x1C
DATA_SIZE = 4

# Dicionário de nomes para action hashes
ACTION_HASH_NAMES = {
    # YKW3 P10 / P80
    "A8 5A 6A 85": "T-pose",
    "4A 09 C3 43": "Idle",
    "44 6A 78 62": "Long idle",
    "A5 CF E5 80": "Talk",
    "B4 27 F7 FF": "Walk P10",
    "54 43 28 60": "Run P10",
    "20 33 E6 11": "???",
    
    # YKW3 P20
    "58 DF 5B 84": "Battle start animation",
    "2F 60 5C C8": "Idle Animation",
    "17 94 B0 2D": "Long Idle Animation",
    "23 8F 2C 41": "Tired/Sleeping Animation",
    "F8 E2 EE 80": "Loafing Animation",
    "7E 15 40 AB": "Recovering Animation",
    "98 12 A9 9B": "Attack Animation",
    "4D 03 C3 B7": "Magic/Inspirit Animation",
    "B1 01 4E 48": "Guard Animation",
    "CD 2A A7 DA": "Miss Animation",
    "D6 D6 8B 14": "Damage Animation",
    "B1 85 81 B5": "Death Animation",
    "A9 E0 BB 11": "Last Frame of Death Animation/Ascension",
    "04 B7 C0 F9": "Charge Animation",
    "54 53 5B 79": "Soultimate Start Animation",
    "0A 8E 77 DE": "Soultimate animation",

    # YKW3 P21
    "AB 00 7C 21": "Victory Dance 1 Start",
    "56 E4 4D EC": "Victory Dance 1",
    "11 51 75 B8": "Victory Dance 2 Start",
    "95 B7 60 C7": "Victory Dance 2",
    "87 61 72 CF": "Victory Dance 3 Start",
    "D4 86 7B DE": "Victory Dance 3",
    "24 F4 16 51": "Victory Dance 4 Start",
    "13 10 3A 91": "Victory Dance 4",

    # Blasters P84
    "C2 B2 3B F0": "Walk",
    "22 D6 E4 6F": "Run",
    "3C 9C 0F 4C": "Idle Animation",
    "B8 32 75 BC": "Long Idle Animation",
    "30 73 7F C5": "Tired/Sleeping Animation",
    "6D D8 FD 46": "Recovering Animation",
    "47 7A AA 9D": "Guard Animation",
    "DE E7 1A 37": "Victory Dance 1",
    "84 65 80 40": "Damage Animation",
    "76 16 E5 FB": "Death Animation",
    "29 D3 F5 14": "Last Frame of Death Animation/Ascension",
    "B8 CD C1 CC": "Victory Dance 2",
    "45 18 1E 68": "Victory Dance 3",
    "17 4B 93 7D": "Charge Animation",
    "CA A1 A2 CF": "Attack Animation",
    "09 A4 F3 67": "Power/Charge Attack",
    "70 F0 AB 56": "Triple Attack - Hit 2",
    "E6 C0 AC 21": "Triple Attack - Hit 3",
    "85 CC 3B 21": "Dash Attack",
    "38 BC 48 02": "Fall Back Attack",
    "A6 8A 26 6D": "Magic/Buff/Debuff",
    "06 E0 50 2D": "Soultimate Attack",
    "BF F1 3A D5": "Miss/Dodge Animation",

    # P90
    "70 35 34 1C": "???"
}

class MinfBatchEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Mtninf2TXT")
        
        self.export_button = tk.Button(root, text="Export Info to TXT", command=self.export_info)
        self.export_button.grid(row=0, column=0, padx=10, pady=10)

        self.import_button = tk.Button(root, text="Import Info from TXT", command=self.import_info)
        self.import_button.grid(row=0, column=1, padx=10, pady=10)

        self.info_label = tk.Label(root, text="""Make sure the .mtninf files are in the selected folder.
        Mtninf2TXT by Math_kk
        Original tool by Kirasnuggets""", wraplength=400, justify="center", fg="blue")
        self.info_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    
    def export_info(self):
        folder = filedialog.askdirectory(title="Select Folder with MTNINF Files")
        if not folder:
            return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not save_path:
            return
        
        try:
            exported_data = []
            for filename in os.listdir(folder):
                if filename.endswith(".mtninf"):
                    filepath = os.path.join(folder, filename)
                    with open(filepath, "rb") as file:
                        data = file.read()
                    
                    if len(data) >= FRAME_END + DATA_SIZE:
                        start_frame = struct.unpack_from("<I", data, FRAME_START)[0]
                        end_frame = struct.unpack_from("<I", data, FRAME_END)[0]
                        action_hash = data[ACTION:ACTION + DATA_SIZE]
                        action_str = " ".join(f"{b:02X}" for b in action_hash)
                        action_name = ACTION_HASH_NAMES.get(action_str, "Unknown")
                        exported_data.append(f"{filename} - {action_str} - {action_name} - {start_frame} - {end_frame}")
            
            with open(save_path, "w") as txt_file:
                txt_file.write("\n".join(exported_data))
            
            messagebox.showinfo("Success", f"Exported info to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export info: {e}")
    
    def import_info(self):
        folder = filedialog.askdirectory(title="Select Folder with MTNINF Files")
        if not folder:
            return
        
        txt_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not txt_path:
            return
        
        try:
            with open(txt_path, "r") as txt_file:
                lines = txt_file.readlines()
            
            for line in lines:
                parts = line.strip().split(" - ")
                if len(parts) not in (4, 5):  # Allow lines with or without action_name
                    continue
                
                filename = parts[0]
                action_str = parts[1]
                start_frame = parts[-2]
                end_frame = parts[-1]
                filepath = os.path.join(folder, filename)
                
                if not os.path.isfile(filepath):
                    print(f"File not found: {filepath}")
                    continue
                
                try:
                    with open(filepath, "rb") as file:
                        data = bytearray(file.read())
                    
                    struct.pack_into("<I", data, FRAME_START, int(start_frame))
                    struct.pack_into("<I", data, FRAME_END, int(end_frame))
                    
                    action_hash = bytes.fromhex(action_str.replace(" ", ""))
                    if len(action_hash) != 4:
                        raise ValueError(f"Invalid Action Hash in {filename}")
                    
                    data[ACTION:ACTION + DATA_SIZE] = action_hash
                    
                    with open(filepath, "wb") as file:
                        file.write(data)
                except Exception as e:
                    print(f"Failed to update {filename}: {e}")
            
            messagebox.showinfo("Success", "Imported info and updated files successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import info: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MinfBatchEditor(root)
    root.mainloop()
