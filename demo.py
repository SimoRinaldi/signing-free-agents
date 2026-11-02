import os
import sys
import platform
import subprocess
from pathlib import Path
import pandas as pd

from src.core.models import RosterSolution
from src.core.loader import load_scenario
from src.benchmark.exporter import DataExporter
from src.algorithms.optimal_value import (
    compute_optimal_war,
    compute_optimal_war_without_s,
)
from src.algorithms.optimal_solution import (
    reconstruct_optimal_roster,
    reconstruct_optimal_roster_without_s,
)
from src.algorithms.space_optimized import compute_optimal_war_with_one_vector
from src.algorithms.time_optimized import compute_optimal_war_with_recursion
from src.algorithms.filter import filter_players


exporter = DataExporter(output_dir="results")


def clear_screen():
    """Pulisce il terminale."""
    os.system("clear" if os.name != "nt" else "cls")


def pause():
    """Attende che l'utente prema Invio prima di tornare al menu."""
    input("\nPremi [Invio] per tornare al menu...")


def print_header(scenario):
    """Pulisce lo schermo e stampa l'intestazione fissa con i dati dello scenario."""
    clear_screen()
    print("PROGETTO ALGORITMI: SIGNING FREE-AGENT PLAYERS")
    print(f"Scenario: {scenario.name} | Ruoli (N)={scenario.N} | Budget (B)={scenario.B} (${scenario.budget:,.0f}) | Candidati (P)={scenario.P}\n")


def open_file_in_os(filepath):
    """Apre un file con il visualizzatore predefinito in modo multipiattaforma (Linux, Windows, macOS)."""
    path = Path(filepath)
    if not path.exists():
        print(f"\n[Avviso] Il file '{path.name}' non esiste ancora in 'results/'.")
        print("Esegui prima il benchmark per generarlo.")
        return

    system_name = platform.system()
    try:
        if system_name == "Windows":
            os.startfile(str(path))
        elif system_name == "Darwin":  # macOS
            subprocess.run(["open", str(path)], check=True)
        else:  # Linux / POSIX
            subprocess.run(["xdg-open", str(path)], check=True)
        print(f"\nAperto con successo: '{path.name}'")
    except Exception as e:
        print(f"\nImpossibile aprire automaticamente il file: {e}")
        print(f"Puoi visualizzarlo manualmente in: {path.resolve()}")


def get_available_scenarios():
    scenarios_dir = Path("scenarios")
    return sorted(scenarios_dir.glob("*.json"))


def print_roster_dataframe(scenario, solution: RosterSolution):
    """Formatta e stampa la rosa ottimale usando la classe RosterSolution."""
    print("ROSA TITOLARE OTTIMALE:\n")

    players_by_role = {}
    for p in solution.players:
        for r in scenario.roles:
            if any(c.name == p.name for c in r.candidates):
                players_by_role[r.name] = p
                break

    headers = ["Ruolo", "Giocatore Ingaggiato", "Costo ($)", "WAR"]
    alignments = ["left", "left", "right", "right"]
    rows = []

    for r in scenario.roles:
        p = players_by_role.get(r.name)
        if p:
            rows.append([r.name, p.name, f"${p.cost:,.0f}", f"+{p.war:.1f}"])
        else:
            rows.append([r.name, "(Nessun ingaggio)", "$0", "0.0"])

    print(exporter.format_box_table(headers, rows, alignments))

    percentuale_spesa = (solution.total_cost / scenario.budget) * 100 if scenario.budget > 0 else 0
    print(f"\nRiepilogo Economico:")
    print(f"  • Valore Ottimo (WAR Totale):   ★ {solution.optimal_war:.1f} (valore della cella m[N, B])")
    print(f"  • Budget Iniziale:          ${scenario.budget:,.0f}")
    print(f"  • Spesa Effettiva:          ${solution.total_cost:,.0f} ({percentuale_spesa:.1f}% del budget)")
    print(f"  • Budget Residuo:           ${scenario.budget - solution.total_cost:,.0f}")


def print_matrices_dataframe(scenario, m, s):
    """Formatta e stampa le matrici m ed s evidenziando il valore ottimo e il passo di ricostruzione."""
    role_labels = ["Base (i=0)"] + [f"{r.name} (i={idx})" for idx, r in enumerate(scenario.roles, 1)]
    max_cols = 10
    limit_cols = min(scenario.B + 1, max_cols)
    col_labels = [f"b={b}" for b in range(limit_cols)]

    if scenario.B >= max_cols:
        print(f"[Nota: Budget B={scenario.B} elevato; visualizzazione limitata alle prime {limit_cols} colonne]")
        print(f"[La matrice integrale di {scenario.N + 1}×{scenario.B + 1} celle è disponibile in results/matrice_m_{scenario.name}.csv]\n")

    m_sub = [row[:limit_cols] for row in m]
    s_sub = [row[:limit_cols] for row in s]

    # Se l'intera matrice rientra a video, evidenziamo l'angolo in basso a destra (N, B)
    highlight = (scenario.N, scenario.B) if scenario.B < max_cols else None

    print("Matrice dei Valori Ottimi (m):")
    print(exporter.format_matrix(m_sub, row_labels=role_labels, col_labels=col_labels, highlight_cell=highlight))

    print("\nMatrice delle Decisioni (s) [-1 = nessun acquisto]:")
    print(exporter.format_matrix(s_sub, row_labels=role_labels, col_labels=col_labels, highlight_cell=highlight))

    optimal_war = m[scenario.N][scenario.B]
    s_val = s[scenario.N][scenario.B]
    last_role = scenario.roles[scenario.N - 1]

    print("\n" + "=" * 74)
    print("★ INTERPRETAZIONE E LOCALIZZAZIONE DEL VALORE OTTIMO (Compito 1 e 2):")
    print("=" * 74)
    if scenario.B < max_cols:
        print(f"1. VALORE OTTIMO GLOBALE: cella m[N, B] = m[{scenario.N}, {scenario.B}] = {optimal_war:.1f} WAR")
        print(f"   • Collocazione: angolo in basso a destra della tabella m (evidenziata con '★ {optimal_war:.1f}').")
        print(f"   • Significato: rappresenta il massimo WAR ottenibile considerando tutti gli N={scenario.N} ruoli")
        print(f"     con il budget complessivo a disposizione B={scenario.B} (${scenario.budget:,.0f}).")
        print()
        print(f"2. PUNTO DI PARTENZA RICOSTRUZIONE: cella s[N, B] = s[{scenario.N}, {scenario.B}] = {s_val}")
        print(f"   • Collocazione: angolo in basso a destra della tabella s (evidenziata con '★ {s_val}').")
        print(f"   • La procedura 'Reconstruct-Optimal-Roster' risale a ritroso esattamente da qui:")
        if s_val >= 0:
            cand = last_role.candidates[s_val]
            scaled_cost = int(cand.cost / scenario.cost_unit)
            rem_b = scenario.B - scaled_cost
            prev_role_name = scenario.roles[scenario.N - 2].name if scenario.N > 1 else "Base"
            print(f"     - Per il ruolo {scenario.N} ({last_role.name}) è stato ingaggiato il candidato #{s_val}:")
            print(f"       '{cand.name}' (costo: ${cand.cost:,.0f}, WAR: +{cand.war:.1f});")
            print(f"     - Il budget residuo per i ruoli precedenti diventa: b = {scenario.B} - {scaled_cost} = {rem_b};")
            print(f"     - L'algoritmo passa quindi alla riga precedente i={scenario.N - 1} ({prev_role_name}) alla colonna b={rem_b},")
            print(f"       proseguendo all'indietro fino alla riga base (i=0).")
        else:
            print(f"     - Per il ruolo {scenario.N} ({last_role.name}) nessun giocatore è stato ingaggiato (s=-1);")
            print(f"     - Il budget residuo resta b = {scenario.B}, passando alla riga precedente i={scenario.N - 1}.")
    else:
        print(f"1. VALORE OTTIMO GLOBALE: cella m[N, B] = m[{scenario.N}, {scenario.B}] = {optimal_war:.1f} WAR")
        print(f"   • Collocazione: si trova all'angolo terminale in basso a destra dell'intera matrice:")
        print(f"     riga i={scenario.N} ({last_role.name}), colonna b={scenario.B} (${scenario.budget:,.0f}).")
        print(f"   • Nota: data la dimensione di B={scenario.B}, a video sono mostrate solo le prime {limit_cols} colonne.")
        print(f"     La matrice completa di tutte le {scenario.N + 1}×{scenario.B + 1} celle è ispezionabile in:")
        print(f"     'results/matrice_m_{scenario.name}.csv'")
        print()
        print(f"2. RICOSTRUZIONE DELLA ROSA: cella s[N, B] = s[{scenario.N}, {scenario.B}] = {s_val}")
        print(f"   • La procedura a ritroso 'Reconstruct-Optimal-Roster' parte dalla cella terminale s[{scenario.N}, {scenario.B}]")
        print(f"     e scala i ruoli fino a i=0 per determinare la formazione completa.")
    print("=" * 74)


def run_coherence_comparison(scenario):
    """Confronta tutte le varianti algoritmiche dimostrando la coerenza del risultato."""
    print("CONFRONTO TRA VARIANTI E VERIFICA DI COERENZA:\n")
    N, X, players = scenario.N, scenario.budget, scenario.get_players_matrix()
    cost_unit = scenario.cost_unit

    # 1. Bottom-up con matrice s
    opt_war_s, s = compute_optimal_war(N, X, players, cost_unit)
    roster_s, cost_s = reconstruct_optimal_roster(N, X, players, s, cost_unit)

    # 2. Bottom-up senza matrice s (solo m)
    opt_war_no_s, m = compute_optimal_war_without_s(N, X, players, cost_unit)
    roster_no_s, cost_no_s = reconstruct_optimal_roster_without_s(N, X, players, m, cost_unit)

    # 3. Bottom-up vettore singolo
    opt_war_vec = compute_optimal_war_with_one_vector(N, X, players, cost_unit)

    # 4. Top-Down ricorsivo
    opt_war_td = compute_optimal_war_with_recursion(N, X, players, cost_unit)

    # 5. Bottom-up con Filtro di Pareto
    filtered = filter_players(players, cost_unit, scenario.B)
    opt_war_filter, m_fil = compute_optimal_war_without_s(N, X, filtered, cost_unit)
    roster_fil, cost_fil = reconstruct_optimal_roster_without_s(N, X, filtered, m_fil, cost_unit)

    headers = ["Variante Algoritmica", "WAR Ottimo", "Spesa Totale", "Acquisti"]
    alignments = ["left", "right", "right", "center"]
    rows = [
        ["Bottom-Up (con matrice s)", f"{opt_war_s:.1f}", f"${cost_s:,.0f}", str(len(roster_s))],
        ["Bottom-Up (solo matrice m)", f"{opt_war_no_s:.1f}", f"${cost_no_s:,.0f}", str(len(roster_no_s))],
        ["Bottom-Up (vettore singolo)", f"{opt_war_vec:.1f}", "(solo valore)", "-"],
        ["Top-Down (memoizzato)", f"{opt_war_td:.1f}", "(solo valore)", "-"],
        ["Bottom-Up + Filtro Pareto", f"{opt_war_filter:.1f}", f"${cost_fil:,.0f}", str(len(roster_fil))],
    ]

    print(exporter.format_box_table(headers, rows, alignments))

    coincidono = (abs(opt_war_s - opt_war_no_s) < 1e-9 and 
                  abs(opt_war_s - opt_war_vec) < 1e-9 and 
                  abs(opt_war_s - opt_war_td) < 1e-9 and 
                  abs(opt_war_s - opt_war_filter) < 1e-9)

    print()
    if coincidono:
        print("Esito: [CONFERMATO] Tutte le 5 varianti calcolano esattamente lo stesso WAR ottimo.")
    else:
        print("Esito: [AVVISO] Sono state riscontrate discrepanze numeriche.")


def graphs_menu(scenario):
    """Sotto-menu per aprire i grafici prestazionali in modo multipiattaforma."""
    results_dir = Path("results")
    while True:
        print_header(scenario)
        print("GRAFICI PRESTAZIONALI E BENCHMARK (Compito 3):\n")
        print("1. Apri Grafico Valore Ottimo (Tempo e Memoria)")
        print("2. Apri Grafico Ricostruzione (Memoria: matrice s vs matrice m)")
        print("3. Apri Tabella Comparativa Prestazioni (PNG)")
        print("0. Torna al menu principale\n")

        sub_choice = input("Seleziona un'opzione [0-3]: ").strip()

        if sub_choice == "1":
            open_file_in_os(results_dir / "plot_optimal_value.png")
            pause()
        elif sub_choice == "2":
            open_file_in_os(results_dir / "plot_reconstruction_memory.png")
            pause()
        elif sub_choice == "3":
            open_file_in_os(results_dir / "table_algorithms_comparison.png")
            pause()
        elif sub_choice == "0":
            break


def interactive_menu():
    scenarios = get_available_scenarios()
    if not scenarios:
        print("Errore: Nessun scenario trovato nella cartella 'scenarios/'.")
        sys.exit(1)

    current_idx = 0
    for idx, path in enumerate(scenarios):
        if "scenario_00" in path.stem or "demo" in path.stem:
            current_idx = idx
            break

    while True:
        scenario = load_scenario(scenarios[current_idx])
        print_header(scenario)

        print("1. Mostra Rosa Titolare Ottimale")
        print("2. Ispeziona Matrici Dinamiche (m ed s)")
        print("3. Confronta Tutte le Varianti Algoritmiche")
        print("4. Cambia Scenario")
        print("5. Grafici Prestazionali e Benchmark (Compito 3)")
        print("0. Esci\n")

        choice = input("Seleziona un'opzione [0-5]: ").strip()

        if choice == "1":
            print_header(scenario)
            N, X, players = scenario.N, scenario.budget, scenario.get_players_matrix()
            optimal_war, s = compute_optimal_war(N, X, players, scenario.cost_unit)
            signed_players, total_cost = reconstruct_optimal_roster(
                N, X, players, s, scenario.cost_unit
            )
            solution = RosterSolution(
                optimal_war=optimal_war,
                players=signed_players,
                total_cost=total_cost,
            )
            print_roster_dataframe(scenario, solution)
            pause()

        elif choice == "2":
            print_header(scenario)
            N, X, players = scenario.N, scenario.budget, scenario.get_players_matrix()
            _, s = compute_optimal_war(N, X, players, scenario.cost_unit)
            _, m = compute_optimal_war_without_s(N, X, players, scenario.cost_unit)
            print_matrices_dataframe(scenario, m, s)
            pause()

        elif choice == "3":
            print_header(scenario)
            run_coherence_comparison(scenario)
            pause()

        elif choice == "4":
            print_header(scenario)
            print("Scenari disponibili:\n")
            for idx, path in enumerate(scenarios):
                mark = " (selezionato)" if idx == current_idx else ""
                demo_lbl = " (demo)" if "scenario_00" in path.stem else ""
                print(f"  [{idx + 1}] {path.name}{demo_lbl}{mark}")
            sel = input(f"\nScegli il numero dello scenario [1-{len(scenarios)}]: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(scenarios):
                current_idx = int(sel) - 1
                print(f"\nScenario impostato: {scenarios[current_idx].name}")
                pause()

        elif choice == "5":
            graphs_menu(scenario)

        elif choice == "0":
            clear_screen()
            print("Chiusura della demo.\n")
            break


def main():
    clear_screen()
    print("PROGETTO ALGORITMI: SIGNING FREE-AGENT PLAYERS")
    print("Modellazione e Risoluzione tramite Programmazione Dinamica\n")
    print("Fase 1: Esecuzione del processo di calcolo ed elaborazione degli scenari.")
    print("        (Vengono eseguiti gli algoritmi, calcolate le metriche ed esportati i file di output)\n")

    scelta = input("Avviare l'elaborazione su tutti gli scenari? [S/n]: ").strip().lower()
    if scelta not in ("n", "no"):
        print()
        from main import main as run_batch_benchmarks
        run_batch_benchmarks()
        print("\nElaborazione completata con successo!")
        input("\nPremi [Invio] per accedere al menu interattivo della demo...")

    interactive_menu()


if __name__ == "__main__":
    main()
