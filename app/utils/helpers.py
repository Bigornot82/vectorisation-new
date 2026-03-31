"""
Helpers - Fonctions utilitaires.
"""

import os
from pathlib import Path


def ensure_output_dir(base_dir: str = "output") -> str:
    """
    Crée le répertoire de sortie s'il n'existe pas.

    Args:
        base_dir: Répertoire de base

    Returns:
        Chemin du répertoire de sortie
    """
    output_dir = Path(base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)


def get_unique_filename(filepath: str) -> str:
    """
    Génère un nom de fichier unique si le fichier existe déjà.

    Args:
        filepath: Chemin du fichier

    Returns:
        Chemin unique
    """
    if not os.path.exists(filepath):
        return filepath

    path = Path(filepath)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return str(new_path)
        counter += 1


def open_folder(folder_path: str) -> None:
    """
    Ouvre un dossier dans l'explorateur de fichiers.

    Args:
        folder_path: Chemin du dossier
    """
    import subprocess
    import platform

    folder_path = str(Path(folder_path).absolute())

    if not os.path.exists(folder_path):
        return

    system = platform.system()

    try:
        if system == "Darwin":  # macOS
            subprocess.Popen(["open", folder_path])
        elif system == "Windows":
            os.startfile(folder_path)
        else:  # Linux et autres
            subprocess.Popen(["xdg-open", folder_path])
    except Exception as e:
        print(f"Erreur lors de l'ouverture du dossier : {e}")


def rgb_to_hex(rgb: tuple) -> str:
    """
    Convertit un tuple RGB en couleur hex.

    Args:
        rgb: Tuple (R, G, B)

    Returns:
        String hex (#RRGGBB)
    """
    return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convertit une couleur hex en RGB.

    Args:
        hex_color: String hex (#RRGGBB)

    Returns:
        Tuple (R, G, B)
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
