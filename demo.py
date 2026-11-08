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
    clear_screen()
    print("\033[1;34mMENU - Signing Free-Agent Players\033[0m\n")
    print(f"\033[1;36m{scenario.name}\033[0m | Ruoli N={scenario.N} | Budget B=${scenario.budget:,.0f} | Candidati P={scenario.P}\033[0m\n")


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


def print_roster(scenario, solution: RosterSolution):
    print("ROSA OTTIMALE:\n")

    players_by_role = {}
    for p in solution.players:
        for r in scenario.roles:
            if any(c.name == p.name for c in r.candidates):
                players_by_role[r.name] = p
                break

    headers = ["Ruolo", "Giocatore ingaggiato", "Costo ($)", "WAR"]
    alignments = ["center", "center", "center", "center"]
    rows = []

    for r in scenario.roles:
        p = players_by_role.get(r.name)
        if p:
            rows.append([r.name, p.name, f"${p.cost:,.0f}", f"+{p.war:.1f}"])
        else:
            rows.append([r.name, "(Nessun ingaggio)", "$0", "0.0"])

    print(exporter.format_box_table(headers, rows, alignments))

    percentuale_spesa = (solution.total_cost / scenario.budget) * 100 if scenario.budget > 0 else 0
    print(f"\nRiepilogo:")
    print(f"  • WAR ottimo:               {solution.optimal_war:.1f}")
    print(f"  • Budget iniziale:          ${scenario.budget:,.0f}")
    print(f"  • Spesa effettiva:          ${solution.total_cost:,.0f} ({percentuale_spesa:.1f}% del budget)")
    print(f"  • Budget residuo:           ${scenario.budget - solution.total_cost:,.0f}")


def print_matrices(scenario, m, s):
    role_labels_m = [""] + [
        f"{r.name}" for _, r in enumerate(scenario.roles, 1)
    ] 

    role_labels_s = [""] + [
        f"{r.name}" for _, r in enumerate(scenario.roles, 1)
    ] 

    max_cols = 8
    if scenario.B + 1 <= max_cols:
        col_labels = [f"b={b}" for b in range(scenario.B + 1)]
        m_sub = m
        s_sub = s
        highlight_m = (scenario.N, scenario.B)
    else:
        head_indices = list(range(4))
        tail_indices = list(range(scenario.B - 3, scenario.B + 1))

        col_labels = [f"b={b}" for b in head_indices] + ["..."] + [f"b={b}" for b in tail_indices]

        m_sub = [
            [row[b] for b in head_indices] + ["..."] + [row[b] for b in tail_indices]
            for row in m
        ]

        s_sub = [
            [row[b] for b in head_indices] + ["..."] + [row[b] for b in tail_indices]
            for row in s
        ]

        highlight_m = (scenario.N, len(m_sub[0]) - 1)

        print(f"[Nota: Budget B={scenario.B} elevato, visualizzazione limitata alle prime 4 e ultime 4 colonne]\n")

    print("Tabella m (per il calcolo del WAR ottimo):")
    print(exporter.format_matrix(m_sub, row_labels=role_labels_m, col_labels=col_labels, highlight_cell=highlight_m))

    print("\nTabella s (per la ricostruzione della rosa ottima):")
    print(exporter.format_matrix(s_sub, row_labels=role_labels_s, col_labels=col_labels, highlight_cell=None))
    print("(-1 = nessun acquisto), (>=0 = indice del giocatore selezionato per il ruolo corrispondente)")

def run_variants_comparison(scenario):
    print("CONFRONTO TRA VARIANTI ALGORITMICHE:\n")
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

    # 5. Bottom-up con filtro
    filtered = filter_players(players, cost_unit, scenario.B)
    opt_war_filter, m_fil = compute_optimal_war_without_s(N, X, filtered, cost_unit)
    roster_fil, cost_fil = reconstruct_optimal_roster_without_s(N, X, filtered, m_fil, cost_unit)

    # 6. Bottom-up vettore singolo + filtro
    opt_war_filter_vec = compute_optimal_war_with_one_vector(N, X, filtered, cost_unit)

    headers = ["", "WAR ottimo", "Spesa totale", "Acquisti"]
    alignments = ["center", "center", "center", "center"]
    rows = [
        ["Bottom-Up (con matrice s)", f"{opt_war_s:.1f}", f"${cost_s:,.0f}", str(len(roster_s))],
        ["Bottom-Up (solo matrice m)", f"{opt_war_no_s:.1f}", f"${cost_no_s:,.0f}", str(len(roster_no_s))],
        ["Bottom-Up (vettore singolo)", f"{opt_war_vec:.1f}", "-", "-"],
        ["Top-Down (ricorsivo)", f"{opt_war_td:.1f}", "-", "-"],
        ["Bottom-Up (con filtro)", f"{opt_war_filter:.1f}", f"${cost_fil:,.0f}", str(len(roster_fil))],
        ["Bottom-Up (vettore singolo + filtro)", f"{opt_war_filter_vec:.1f}", "-", "-"],
    ]

    print(exporter.format_box_table(headers, rows, alignments))

    coincidono = (abs(opt_war_s - opt_war_no_s) < 1e-9 and 
                  abs(opt_war_s - opt_war_vec) < 1e-9 and 
                  abs(opt_war_s - opt_war_td) < 1e-9 and 
                  abs(opt_war_s - opt_war_filter) < 1e-9 and
                  abs(opt_war_s - opt_war_filter_vec) < 1e-9)

    print()
    if coincidono:
        print("SUCCESSO! Tutte le varianti calcolano lo stesso WAR ottimo.")
    else:
        print("AVVISO! Non tutte le varianti calcolano lo stesso WAR ottimo.")


def graphs_menu(scenario):
    results_dir = Path("results")
    while True:
        print_header(scenario)
        print("GRAFICI E BENCHMARK DELLE PRESTAZIONI:\n")
        print("1. Apri grafico calcolo WAR ottimo")
        print("2. Apri grafico ricostruzione rosa ottima")
        print("3. Apri tabella comparativa prestazioni")
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

        print("1. Mostra rosa ottimale")
        print("2. Visualizza tabelle")
        print("3. Confronta le varianti algoritmiche")
        print("4. Cambia scenario")
        print("5. Grafici e benchmark delle prestazioni")
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
            print_roster(scenario, solution)
            pause()

        elif choice == "2":
            print_header(scenario)
            N, X, players = scenario.N, scenario.budget, scenario.get_players_matrix()
            _, s = compute_optimal_war(N, X, players, scenario.cost_unit)
            _, m = compute_optimal_war_without_s(N, X, players, scenario.cost_unit)
            print_matrices(scenario, m, s)
            pause()

        elif choice == "3":
            print_header(scenario)
            run_variants_comparison(scenario)
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
    print("\033[1;34mDEMO PROGETTO ALGORITMI E STRUTTURE DATI - Programmazione Dinamica\033[0m\n")
    print("Problema: \033[1;32mSigning Free-Agent Players\033[0m\n")

    while True:
        choice = input("Avviare l'elaborazione su tutti gli scenari di test? [s/n]: ").strip().lower()
        if choice in ("s", "si"):
            from main import run_all_scenarios
            print()
            run_all_scenarios()
            input("\nPremi [Invio] per accedere al menu...")
            break
        elif choice in ("n", "no"):
            input("\nPremi [Invio] per accedere al menu...")
            break
        
    interactive_menu()


if __name__ == "__main__":
    main()
