import subprocess
import sys
import os
import pkg_resources
import ctypes

requirements_file = "requirements.txt"

def install_missing_packages():
    with open(requirements_file) as f:
        required = f.read().splitlines()

    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = []

    for requirement in required:
        if requirement.strip() and not requirement.strip().startswith("#"):
            pkg_name = requirement.strip().split("==")[0].lower()
            if pkg_name not in installed:
                missing.append(requirement.strip())

    if missing:
        print("Instalowanie brakujących pakietów:")
        for pkg in missing:
            print(f"  → {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

if os.path.exists(requirements_file):
    install_missing_packages()

hide_console()

print("Aby całkowicie wylaczyc aplikacje, prosze zamknac to okno\n")

subprocess.Popen(["streamlit", "run", "Home.py", "--server.runOnSave=false"])

