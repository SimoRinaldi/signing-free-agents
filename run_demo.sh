#!/bin/bash
# Script di avvio rapido per la Demo degli Algoritmi
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Attivazione dell'ambiente virtuale se presente
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Avvio della demo interattiva
python3 demo.py
