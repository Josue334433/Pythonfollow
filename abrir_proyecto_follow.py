import subprocess
import os
import webbrowser
import tkinter as tk
from tkinter import messagebox, Toplevel, Label
from threading import Thread
import time
import shutil
import glob
import socket

# Ruta a XAMPP
xampp_path = r"C:\xampp\xampp_start.exe"
xampp_stop_path = r'C:\xampp\xampp_stop.exe'
# Ruta al proyecto de Laravel
laravel_project_path_2 = r"C:\xampp\htdocs\IdebApp"
# Ruta al icono   
icon_path = r'C:\xampp\htdocs\fav.ico'

# Flag to check if the project is already running
project_running = False

def abrir_xampp():
    try:
        subprocess.Popen(xampp_path, shell=True)
        print("XAMPP iniciado.")
    except Exception as e:
        print(f"Error al iniciar XAMPP: {e}")
        messagebox.showerror("Error", f"Error al iniciar XAMPP: {e}")

def abrir_laravel_proyecto(path):
    try:
        os.chdir(path)
        subprocess.Popen(["cmd", "/K", "php artisan serve"], shell=True)
        print("Proyecto Laravel iniciado en 127.0.0.1:8000.")
    except Exception as e:
        print(f"Error al iniciar el proyecto en {path}: {e}")
        messagebox.showerror("Error", f"Error al iniciar el proyecto en {path}: {e}")

def verificar_servidor(ip, puerto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((ip, puerto))
        sock.close()
        return True
    except socket.error:
        return False

def esperar_servidor(ip, puerto, max_intentos=20):
    intentos = 0
    while intentos < max_intentos:
        if verificar_servidor(ip, puerto):
            return True
        intentos += 1
        time.sleep(1)
    return False

def limpiar_directorio_temp():
    temp_dir = os.path.join(os.getenv('TEMP'), "MEI*")
    try:
        for temp_subdir in glob.glob(temp_dir):
            if os.path.isdir(temp_subdir):
                shutil.rmtree(temp_subdir, ignore_errors=True)
                print(f"Directorio temporal eliminado: {temp_subdir}")
    except Exception as e:
        print(f"Error al limpiar directorios temporales: {e}")

def iniciar_proyecto():
    global project_running
    if project_running:
        messagebox.showwarning("Advertencia", "El proyecto ya está corriendo.")
        return

    waiting_window = Toplevel(root)
    waiting_window.title("Espera")
    waiting_window.geometry("300x100")
    waiting_window.iconbitmap(icon_path)
    waiting_window.configure(bg='#2b2b2b')
    Label(waiting_window, text="Espera mientras se abre el proyecto...", bg='#2b2b2b', fg='#ffffff', font=("Helvetica", 12)).pack(pady=20)
    
    root.update_idletasks()
    x = root.winfo_x()
    y = root.winfo_y()
    waiting_window.geometry(f"+{x + 100}+{y + 100}")

    def start_project():
        global project_running
        abrir_xampp()
        time.sleep(8)  # Esperar para XAMPP
        abrir_laravel_proyecto(laravel_project_path_2)
        
        if esperar_servidor("127.0.0.1", 8000):
            project_running = True
            waiting_window.destroy()
            messagebox.showinfo("Éxito", "Proyecto iniciado correctamente.")
            webbrowser.open("http://127.0.0.1:8000")
        else:
            waiting_window.destroy()
            messagebox.showerror("Error", "El proyecto no se pudo iniciar correctamente.")

    thread = Thread(target=start_project)
    thread.start()

    # Centrar la ventana de mensaje con la pantalla principal
    waiting_window.update_idletasks()
    ww_width = waiting_window.winfo_width()
    ww_height = waiting_window.winfo_height()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x = root.winfo_x() + (root_width - ww_width) // 2
    y = root.winfo_y() + (root_height - ww_height) // 2
    waiting_window.geometry(f"{ww_width}x{ww_height}+{x}+{y}")

def is_process_running(process_name):
    try:
        result = subprocess.check_output(f'tasklist | findstr {process_name}', shell=True)
        return process_name in result.decode()
    except subprocess.CalledProcessError:
        return False

def cerrar_proyectos():
    global project_running
    try:
        php_running = is_process_running("php.exe")
        xampp_running = is_process_running("xampp-control.exe")  # Cambia "xampp-control.exe" por el nombre correcto si es diferente

        if not php_running and not xampp_running:
            messagebox.showinfo("Estado", "Ningún proyecto ni XAMPP están corriendo.")
            return

        def cerrar_xampp():
            if xampp_running:
                subprocess.Popen(xampp_stop_path, shell=True)
            else:
                print("XAMPP no está corriendo.")

        def cerrar_php():
            if php_running:
                subprocess.Popen("taskkill /f /im php.exe", shell=True)
            else:
                print("PHP no está corriendo.")
        
        # Crear y ejecutar subprocesos para cierre paralelo
        thread_xampp = Thread(target=cerrar_xampp)
        thread_php = Thread(target=cerrar_php)
        
        thread_xampp.start()
        thread_php.start()
        
        # Esperar a que ambos hilos terminen
        thread_xampp.join()
        thread_php.join()
        
        project_running = False
        try:
            limpiar_directorio_temp()  # Limpiar el directorio temporal después de cerrar los procesos
        except Exception as e:
            print(f"Error al limpiar directorios temporales: {e}")
        messagebox.showinfo("Éxito", "Proyecto y XAMPP cerrados correctamente.")
        root.quit()  # Cierra la ventana principal y termina el programa
    except Exception as e:
        print(f"Error al cerrar los proyectos: {e}")
        messagebox.showerror("Error", f"Error al cerrar los proyectos: {e}")

root = tk.Tk()
root.title("Iniciar Proyecto")
root.geometry("500x300")

# Centrar la ventana principal en la pantalla
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 500) // 2
y = (screen_height - 300) // 2
root.geometry(f"500x300+{x}+{y}")
root.configure(bg='#1e1e1e')

try:
    root.iconbitmap(icon_path)
except Exception as e:
    print(f"Error al cargar el icono: {e}")
    messagebox.showerror("Error", f"Error al cargar el icono: {e}")

frame = tk.Frame(root, bg='#1e1e1e')
frame.pack(expand=True)

btn_iniciar = tk.Button(frame, text="Iniciar Proyecto", command=iniciar_proyecto, bg='#2e8b57', fg='#ffffff', font=("Helvetica", 12), relief='flat', padx=20, pady=10)
btn_iniciar.pack(pady=10)

btn_cerrar = tk.Button(frame, text="Cerrar Proyecto", command=cerrar_proyectos, bg='#b22222', fg='#ffffff', font=("Helvetica", 12), relief='flat', padx=20, pady=10)
btn_cerrar.pack(pady=10)

root.mainloop()
