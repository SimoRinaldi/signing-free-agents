# Signing Free-Agent Baseball Players

> **Progetto per il corso di Algoritmi e Strutture Dati**  
> Università degli Studi di Brescia (UniBS) — A.A. 2025/2026  
> **Autori:** Simone Rinaldi, Matteo Legati  
> **Docente:** Prof.ssa Marina Zanella  

---

## 📌 Descrizione del Progetto

Il progetto affronta la modellazione e la risoluzione del problema dell'**ingaggio dei giocatori svincolati** (*Signing Free-Agent Baseball Players*), tratto dal **Problema 14-12** del manuale *Introduction to Algorithms* (Cormen et al.).

Nel contesto dell'ottimizzazione combinatoria, il problema si configura come un'istanza del **Multiple-Choice Knapsack Problem (MCKP)**:
- Una squadra di baseball deve massimizzare il proprio rendimento complessivo, misurato tramite la statistica **WAR** (*Wins Above Replacement*).
- È possibile ingaggiare **al massimo un giocatore per ciascuno degli $N$ ruoli** disponibili (nel baseball canonico $N=9$).
- La spesa complessiva non può eccedere un **budget finanziario prefissato** $X$.

Per consentire l'accesso immediato $\Theta(1)$ alle tabelle dinamiche senza errori di approssimazione floating-point, i compensi monetari sono scalati tramite una costante intera $\text{COST\_UNIT} = 100\,000$, riconducendo l'istanza a un budget discreto intero $B = \lfloor X / \text{COST\_UNIT} \rfloor$.

---

## 🧠 Varianti Algoritmiche Implementate

All'interno di `src/algorithms/` sono state implementate e confrontate sei strategie risolutive basate sulla **Programmazione Dinamica**:

1. **Bottom-Up con matrice $s$ (`compute_optimal_war`)**: Approccio tabulare canonico che calcola la matrice dei valori ottimi $m$ e la matrice delle decisioni $s$ di dimensione $(N+1) \times (B+1)$. Consente la ricostruzione immediata della rosa in tempo $O(N)$.
2. **Bottom-Up senza matrice $s$ (`compute_optimal_war_without_s`)**: Ottimizzazione che elimina la matrice $s$, dimezzando l'occupazione di memoria RAM. La rosa ottimale viene ricostruita a ritroso tramite l'equazione di ricorrenza della matrice $m$ in $O(N \cdot P)$.
3. **Bottom-Up a Vettore Singolo (`compute_optimal_war_with_one_vector`)**: Riduce lo spazio di memoria a $O(B)$ operando con un unico array iterato a ritroso. Ideale per calcolare il valore ottimo senza allocare l'intera matrice.
4. **Top-Down con Memoizzazione (`compute_optimal_war_with_recursion`)**: Approccio ricorsivo che calcola ed esplora unicamente i sottoproblemi strettamente necessari a determinare la soluzione finale.
5. **Filtraggio Candidati Dominati (`filter_players`)**: Fase di pre-processing che elimina gli atleti non vantaggiosi (WAR $\le 0$, costo $> B$ o costo maggiore a parità/minor WAR).
6. **Bottom-Up / Vettore con Filtro**: Combinazione delle tecniche di programmazione dinamica con il pruning dei dati, che abbatte i tempi di calcolo mantenendo l'ottimalità globale.

---

## 📁 Struttura della Repository

```text
signing-free-agents/
├── demo.py                 # Applicazione interattiva a terminale con menu
├── main.py                 # Esecutore batch per benchmark completi ed export risultati
├── run_demo.sh / .bat      # Script di avvio rapido (Linux/macOS e Windows)
├── requirements.txt        # Dipendenze Python necessarie
├── scenarios/              # File JSON contenenti gli scenari di test
│   ├── scenario_00_...     # Scenario didattico ridotto (N=3, B=6, P=3) per ispezione
│   └── scenario_01_...     # 10 scenari con dati reali MLB e budget crescente
├── results/                # Output generati (metriche CSV, tabelle m/s, grafici PNG)
├── report/                 # Relazione tecnica completa del progetto in LaTeX
└── src/
    ├── core/               # Data model (Player, Role, Scenario) e JSON loader
    ├── algorithms/         # Implementazioni matematiche pure degli algoritmi
    └── benchmark/          # Profiler di tempo/RAM, esportatore tabelle e generatore grafici
```

---

## 🚀 Installazione e Avvio Rapido

### Requisiti
- Python 3.10 o superiore.

### 1. Configurazione dell'Ambiente Virtuale
```bash
# Clona il repository o spostati nella cartella
cd signing-free-agents

# Crea l'ambiente virtuale
python3 -m venv .venv

# Attiva l'ambiente virtuale
# Su Linux/macOS:
source .venv/bin/activate
# Su Windows (Command Prompt):
.\.venv\Scripts\activate.bat
# Su Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Installa le dipendenze
pip install -r requirements.txt
```

### 2. Avvio della Demo Interattiva
Puoi lanciare la demo tramite gli script di avvio rapido:
- **Linux/macOS:**
  ```bash
  chmod +x run_demo.sh
  ./run_demo.sh
  ```
- **Windows:**
  Doppio clic su `run_demo.bat` oppure da terminale:
  ```cmd
  run_demo.bat
  ```
Oppure direttamente tramite Python:
```bash
python demo.py
```

### 3. Esecuzione Benchmark e Generazione Risultati
Per eseguire il profiling di tutte le varianti su tutti gli scenari e rigenerare i grafici:
```bash
python main.py
```

---

## 📊 Funzionalità della Demo CLI

Dal menu principale di `demo.py` è possibile:
- **Visualizzare la rosa ottimale:** Dettaglio dei giocatori ingaggiati ruolo per ruolo, costo contrattuale, WAR e budget residuo.
- **Ispezionare le matrici dinamiche:** Stampa a griglia Unicode delle tabelle $m$ (valori ottimi) ed $s$ (decisioni), con evidenziazione delle celle terminali.
- **Confronto varianti:** Verifica che tutte le 6 formulazioni convergano esattamente allo stesso valore di WAR ottimo.
- **Cambio scenario:** Passaggio dallo scenario didattico a quelli realistici con budget fino a 800 milioni di dollari.
- **Visualizzazione grafici:** Apertura automatica dei grafici generati tramite il visualizzatore immagini predefinito del sistema.

---

## 📈 Risultati Sperimentali e Output

Tutti i risultati delle elaborazioni vengono archiviati nella cartella `results/`:
- `benchmark_metrics.csv`: Tabella con misurazioni del tempo di CPU (minimo su $K$ ripetizioni) e picco di memoria RAM (`tracemalloc`).
- `plot_optimal_value.png`: Confronto grafico tempo/memoria al variare della dimensione dell'istanza $(N \cdot B \cdot P)$.
- `plot_reconstruction_memory.png`: Confronto del picco di memoria tra la memorizzazione congiunta $(m + s)$ e la sola matrice $m$.
- `table_algorithms_comparison.png`: Tabella comparativa riassuntiva esportata ad alta risoluzione.
- `matrice_m_*.csv` e `matrice_s_*.csv`: Dump completo delle tabelle dinamiche per ogni scenario.
