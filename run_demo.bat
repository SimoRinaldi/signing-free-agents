@echo off
:: Si sposta nella cartella in cui si trova questo script                                                                                                                  
cd /d "%~dp0"

:: Attiva l'ambiente virtuale se presente (su Windows si trova in Scripts)
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

:: Avvia la demo interattiva
python demo.py

:: Evita che la finestra del terminale si chiuda all'improvviso all'uscita
pause