import os
import shutil
import pathlib
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import json


file_types = {
    'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.odg', '.ods', 
                   '.rtf', '.md', '.csv'],
    
    'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.heic', '.raw', 
                 '.ico', '.psd', '.ai'],
    
    'Videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.3gp', '.vob', 
               '.m4v', '.mpg'],
    
    'Música': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.alac', '.aiff', 
               '.opus', '.amr'],
    
    'Archivos comprimidos': ['.zip', '.rar', '.tar', '.gz', '.7z', '.bz2', '.xz', '.iso', 
                             '.jar', '.tgz'],
    
    'Ejecutables': ['.exe', '.msi', '.dmg', '.bat', '.sh', '.app', '.deb', '.rpm', '.ps1'],
    
    'Scripts': ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.rb', '.php', '.pl', '.go', '.rs', 
                '.ts', '.lua', '.sql'],
}

checkboxes = {}

#Decidi mover solo los archivos al final para asi solo creo las carpetas necesarias y no pregunto cada vez si la carpeta existe
to_move = []
undo_move = []



def file_organize(address):
    to_move.clear()
    undo_move.clear()
    try:
        mark_files_to_move(address)
        move_marked_files()
    except Exception as e:
        print(f"[ERROR] No se pudo procesar la carpeta {address}: {e}")

def mark_files_to_move(address):
    
     # Recorro todos los archivos del directorio dado
    for item in pathlib.Path(address).iterdir():
        
        full_path = item
        
        # Si es archivo lo preceso
        if full_path.is_file():
            
            #Saco su extension
            extension = full_path.suffix.lower()
            
            #Flag de movimiento
            moved = False 
            
            for folder_name in selected_types:
                extensions = file_types[folder_name]
                if extension in extensions:
                    target_folder = pathlib.Path(address) / folder_names.get(folder_name, folder_name)
                    to_move.append((full_path, target_folder))
                    moved = True
                    break
                    
            # Si no se movio y esta activado la flag global de otros lo muevo ahi   
            if flag_others and not moved:
                extensions_all = [ext for exts in file_types.values() for ext in exts]
                if extension not in extensions_all:
                    target_folder = pathlib.Path(address) / 'Otros'
                    target_folder.mkdir(exist_ok=True)
                    to_move.append((full_path, target_folder))
 
            
def move_marked_files():
    create_target_folders()
    
    for source, target_folder in to_move:
        
        try:
            target_file = target_folder / source.name
            if not flag_replaceFiles:
                count = 1
                while target_file.exists():
                    new_name = f"{source.stem} ({count}){source.suffix}"
                    target_file = target_folder / new_name
                    count += 1
                   
            shutil.move(str(source), str(target_file))
            undo_move.append((target_file, source))
        except Exception as e:
            print(f"[ERROR] No se pudo mover el archivo {source} a {target_folder}: {e}")

    to_move.clear()


def create_target_folders():

    create_folders = set(target for _, target in to_move)
    for folder in create_folders:
        folder.mkdir(exist_ok=True)
    
def undo_moves(undo_button):
    for source, target in undo_move:
        try:
            shutil.move(source, target)
        except Exception as e:
            print(f"[ERROR] No se pudo deshacer el movimiento del archivo {source} a {target}: {e}")
    undo_move.clear()




# Config

def get_app_path():
    if getattr(sys, 'frozen', False):
        return pathlib.Path(sys.executable).parent
    else:
        return pathlib.Path(__file__).parent

def save_config():
    config = {
        "included_folders": included_folders,
        "selected_types": selected_types,
        "flag_others": flag_others,
        "flag_replaceFiles": flag_replaceFiles,
        "folder_names": folder_names
    }
    config_path = get_app_path() / "config.json"
    with config_path.open('w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_config():
    config_path = get_app_path() / "config.json"
    if config_path.exists():
        with config_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    return {"included_folders": [], "selected_types": [] , "flag_others": True, "flag_replaceFiles": False, "folder_names": {}}



config = load_config()
included_folders = config.get("included_folders", [])
selected_types = config.get("selected_types", [])
flag_others = config.get("flag_others", True)
flag_replaceFiles = config.get("flag_replaceFiles", False)
folder_names = config.get("folder_names", {})


def confirm_selection(window, var_others,var_replaceFiles,name_entries):
    global selected_types
    global flag_others
    global flag_replaceFiles
    selected_types = [name for name, var in checkboxes.items() if var.get()]
    flag_others = var_others.get()
    flag_replaceFiles = var_replaceFiles.get()
    
    for foldername, entry_var in name_entries.items():
        folder_names[foldername] = entry_var.get().strip() or foldername
    window.destroy()

def open_selection_window():
    selection_window = tk.Toplevel(root)
    selection_window.title("Configuración")
    selection_window.configure(bg="#001f3f")
    
    frame = ttk.Frame(selection_window, padding=20)
    frame.pack(fill="both", expand=True)
    
    ttk.Label(frame, text="Seleccione los tipos de archivos a organizar y el nombre de sus carpetas:", background="#001f3f", foreground="white", font=("Segoe UI", 10)).pack(pady=(0, 10))

    name_entries = {}

    for foldername in file_types:
        var = tk.BooleanVar(value=(foldername in selected_types))
        checkbox = ttk.Checkbutton(frame, text=foldername, variable=var, style="TCheckbutton")
        checkbox.pack(anchor='w')
        checkboxes[foldername] = var
        
        entry_var = tk.StringVar(value=folder_names.get(foldername, foldername))
        entry = ttk.Entry(frame, textvariable=entry_var, width=20)
        entry.pack(anchor='w', padx=20, pady=(0, 5))
        name_entries[foldername] = entry_var
       
    ttk.Label(frame, text="Extra").pack()  
        
    var_others = tk.BooleanVar(value=flag_others)
    checkbox_others = ttk.Checkbutton(frame, text="Mover los Archivos que no coincidan con ningun tipo", variable=var_others , style="TCheckbutton")
    checkbox_others.pack(anchor='w')
    
    var_replaceFiles = tk.BooleanVar(value=flag_replaceFiles)
    checkbox_replaceFiles = ttk.Checkbutton(frame, text="Remplazar Archivos con El mismo nombre", variable=var_replaceFiles , style="TCheckbutton")
    checkbox_replaceFiles.pack(anchor='w')
     
    confirm_button = ttk.Button(frame, text="Aceptar", command=lambda: confirm_selection(selection_window,var_others,var_replaceFiles, name_entries)) 
    confirm_button.pack(pady=10)


def add_included_folder():
    folder = filedialog.askdirectory()
    if folder and folder not in included_folders:
        included_folders.append(folder)
        update_included_listbox()

def remove_included_folder():
    selected = included_listbox.curselection()
    if selected:
        folder = included_listbox.get(selected)
        included_folders.remove(folder)
        update_included_listbox()

def update_included_listbox():
    included_listbox.delete(0, tk.END)
    for folder in included_folders:
        included_listbox.insert(tk.END, folder)
        

def organize(button):
    
    button_disable(button, "Organizando...")
    for folder in included_folders:
        file_organize(folder)
        
    root.after(500, lambda: (
        button_enable(button, "Organizar Archivos")
    ))
    
def unorganize(button):
    button_disable(button, "Deshaciendo...")
    undo_moves(button)
    root.after(500, lambda: (
        button_enable(button, "Deshacer Movimiento")
    ))

def button_disable(button, textExec):
    button.config(text=textExec, state="disabled")
    button.update_idletasks()
    
def button_enable(button, textExec):
    button.config(text=textExec, state="normal")
    button.update_idletasks()

#Ventana UI


root = tk.Tk()
root.title("Organizador de Archivos")
root.geometry("400x600")

style = ttk.Style()
style.theme_use("clam")

style.configure("TButton",
                font=("Segoe UI", 10, "bold"),
                padding=8,
                background="#124b85",
                foreground="white")

style.configure("TCheckbutton",
                background="#001f3f",
                foreground="white",
                font=("Segoe UI", 10))

style.map("TButton",
          background=[("active", "#1565c0"), ("disabled", "#F70000")])


style.map("TCheckbutton",
          background=[("active", "#1565c0")])

style.configure("Danger.TButton",
                background="#8b2f2f",
                foreground="white")

style.configure("TLabel",
                background="#001f3f",
                foreground="white",
                font=("Segoe UI", 10))

style.configure("TFrame", background="#001f3f")
style.configure("TLabel", background="#001f3f", foreground="white")


main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")

title_label = ttk.Label(main_frame, text="Organizador de Archivos", font=("Segoe UI", 14, "bold"))
title_label.pack(pady=(0, 15))

buttons_frame = ttk.Frame(main_frame)
buttons_frame.pack(fill="x", pady=5)

ttk.Button(buttons_frame, text="Agregar Carpeta a Incluir", command=add_included_folder).pack(fill="x", pady=4)
ttk.Button(buttons_frame, text="Eliminar Carpeta de Incluir", style="Danger.TButton", command=remove_included_folder).pack(fill="x", pady=4)
ttk.Button(buttons_frame, text="Configuración", command=open_selection_window).pack(fill="x", pady=4)

list_label = ttk.Label(main_frame, text="Carpetas a organizar:")
list_label.pack(pady=(15, 5))

included_listbox = tk.Listbox(main_frame, width=50, height=10, bg="#124b85", fg="white", selectbackground="#1565c0", relief="flat", bd=5)
included_listbox.pack(pady=5, fill="both", expand=True)


organize_button = ttk.Button(main_frame, text="Organizar Archivos", command=lambda: organize(organize_button))
organize_button.pack(fill="x", pady=(10, 5))

undo_button = ttk.Button(main_frame, text="Deshacer Movimiento", command=lambda: unorganize(undo_button))
undo_button.pack(fill="x", pady=(0, 10))



update_included_listbox()
root.protocol("WM_DELETE_WINDOW", lambda: [save_config(), root.destroy()])
root.mainloop()




