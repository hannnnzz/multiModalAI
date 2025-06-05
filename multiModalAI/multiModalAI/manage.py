#!/usr/bin/env python
"""
Utility baris perintah Django untuk menjalankan tugas-tugas administratif.
"""

import os
import sys


def main():
    """
    Fungsi utama untuk menjalankan perintah administratif Django.
    - Menentukan modul pengaturan proyek.
    - Mengeksekusi perintah melalui baris perintah.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiModalAI.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as error:
        raise ImportError(
            "Django tidak dapat diimpor. Pastikan Django sudah terinstal dan "
            "terdaftar di PYTHONPATH. Apakah kamu lupa mengaktifkan virtual environment?"
        ) from error

    # Menjalankan perintah yang diberikan melalui terminal
    execute_from_command_line(sys.argv)


# Memastikan skrip hanya dijalankan langsung, bukan diimpor sebagai modul
if __name__ == "__main__":
    main()
