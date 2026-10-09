from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


# Classe per la generazione dei grafici prestazionali
class PerformancePlotter:
    def __init__(
        self,
        metrics_csv: str = "results/benchmark_metrics.csv",
        output_dir: str = "results",
        log_optimal_val: bool = False,
        log_reconstruction: bool = False,
        log_pareto: bool = False,
        show_plots: bool = False,
    ):
        self.metrics_csv = Path(metrics_csv)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_optimal_val = log_optimal_val
        self.log_reconstruction = log_reconstruction
        self.log_pareto = log_pareto
        self.show_plots = show_plots

    def load_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.metrics_csv)
        df["NB"] = df["N"] * df["B"]
        return df

    # Grafico 1: Confronto tra algoritmi per il calcolo del solo valore ottimo
    def plot_optimal_value_comparison(self):
        df = self.load_data()
        target_algos = [
            ("Bottom Up Solver (solo matrice m)", "royalblue", "o"),
            ("Space Efficient Solver", "forestgreen", "s"),
            ("Top Down Memoized", "darkorange", "^"),
        ]

        fig, (ax_time, ax_mem) = plt.subplots(1, 2, figsize=(14, 5))

        for algo_name, color, marker in target_algos:
            subset = df[df["algorithm"] == algo_name].sort_values("instance_size")
            ax_time.plot(
                subset["instance_size"],
                subset["time_ms"],
                label=algo_name,
                color=color,
                marker=marker,
                linewidth=1.8,
            )
            ax_mem.plot(
                subset["NB"],
                subset["memory_kib"],
                label=algo_name,
                color=color,
                marker=marker,
                linewidth=1.8,
            )

        if self.log_optimal_val:
            ax_time.set_xscale("log")
            ax_time.set_yscale("log")
            ax_mem.set_xscale("log")
            ax_mem.set_yscale("log")

        scale_text = " (Scala Log-Log)" if self.log_optimal_val else ""
        ax_time.set_title(f"Tempo di Calcolo Valore Ottimo{scale_text}")
        ax_time.set_xlabel("Dimensione Istanza (N * B * P)")
        ax_time.set_ylabel("Tempo (ms)")
        ax_time.grid(
            True,
            which="both" if self.log_optimal_val else "major",
            linestyle="--",
            alpha=0.5,
        )
        ax_time.legend()

        ax_mem.set_title(f"Occupazione Memoria RAM{scale_text}")
        ax_mem.set_xlabel("Dimensione Tabella (N * B)")
        ax_mem.set_ylabel("Picco Memoria (KiB)")
        ax_mem.grid(
            True,
            which="both" if self.log_optimal_val else "major",
            linestyle="--",
            alpha=0.5,
        )
        ax_mem.legend()

        plt.tight_layout()
        save_path = self.output_dir / "plot_optimal_value.png"
        plt.savefig(save_path, dpi=300)
        if self.show_plots:
            plt.show()
        plt.close(fig)
        return save_path

    # Grafico 2: Confronto memoria per la ricostruzione (con s vs senza s)
    def plot_reconstruction_comparison(self):
        df = self.load_data()
        fig, ax = plt.subplots(figsize=(8, 5))

        subset_s = df[
            df["algorithm"] == "Bottom Up Solver (con tabella s)"
        ].sort_values("NB")
        subset_no_s = df[
            df["algorithm"] == "Bottom Up Solver (solo matrice m)"
        ].sort_values("NB")

        ax.plot(
            subset_s["NB"],
            subset_s["memory_kib"],
            label="Con matrice s (m + s, ricostruzione O(N))",
            color="firebrick",
            marker="o",
            linewidth=2,
        )
        ax.plot(
            subset_no_s["NB"],
            subset_no_s["memory_kib"],
            label="Senza matrice s (solo m, ricostruzione O(N*P))",
            color="royalblue",
            marker="s",
            linewidth=2,
        )

        if self.log_reconstruction:
            ax.set_xscale("log")
            ax.set_yscale("log")

        scale_text = " (Scala Log-Log)" if self.log_reconstruction else ""
        ax.set_title(f"Occupazione di Memoria per la Ricostruzione{scale_text}")
        ax.set_xlabel("Dimensione Tabella (N * B)")
        ax.set_ylabel("Picco Memoria (KiB)")
        ax.grid(
            True,
            which="both" if self.log_reconstruction else "major",
            linestyle="--",
            alpha=0.5,
        )
        ax.legend()

        plt.tight_layout()
        save_path = self.output_dir / "plot_reconstruction_memory.png"
        plt.savefig(save_path, dpi=300)
        if self.show_plots:
            plt.show()
        plt.close(fig)
        return save_path

    # Grafico 3: Impatto del filtro di Pareto sui tempi di esecuzione
    def plot_pareto_impact(self):
        df = self.load_data()
        fig, ax = plt.subplots(figsize=(8, 5))

        base_bu = df[
            df["algorithm"] == "Bottom Up Solver (solo matrice m)"
        ].sort_values("instance_size")
        pareto_bu = df[
            df["algorithm"] == "Bottom Up Solver (Pareto Pruned)"
        ].sort_values("instance_size")

        ax.plot(
            base_bu["instance_size"],
            base_bu["time_ms"],
            label="Bottom Up (Senza Pareto)",
            color="royalblue",
            marker="o",
            linewidth=2,
        )
        ax.plot(
            pareto_bu["instance_size"],
            pareto_bu["time_ms"],
            label="Bottom Up (Pareto Pruned)",
            color="mediumseagreen",
            marker="^",
            linewidth=2,
        )

        if self.log_pareto:
            ax.set_xscale("log")
            ax.set_yscale("log")

        scale_text = " (Scala Log-Log)" if self.log_pareto else ""
        ax.set_title(f"Impatto del Preprocessing di Pareto sul Tempo{scale_text}")
        ax.set_xlabel("Dimensione Istanza (N * B * P)")
        ax.set_ylabel("Tempo (ms)")
        ax.grid(
            True,
            which="both" if self.log_pareto else "major",
            linestyle="--",
            alpha=0.5,
        )
        ax.legend()

        plt.tight_layout()
        save_path = self.output_dir / "plot_pareto_impact.png"
        plt.savefig(save_path, dpi=300)
        if self.show_plots:
            plt.show()
        plt.close(fig)
        return save_path

    # Genera una tabella grafica di riepilogo comparativo tra gli algoritmi
    def plot_comparison_table(self):
        df = self.load_data()
        scenarios = df["scenario"].unique()

        algo_abbr = {
            "Bottom Up Solver (con tabella s)": "BU (con s)",
            "Bottom Up Solver (solo matrice m)": "BU (senza s)",
            "Space Efficient Solver": "Space Eff.",
            "Top Down Memoized": "Top Down",
            "Bottom Up Solver (Pareto Pruned)": "BU (Pareto)",
            "Space Efficient Solver (Pareto Pruned)": "Space (Pareto)",
        }

        col_labels = [
            "Scenario",
            "N",
            "B",
            "P",
            "BU (con s)\nTime | Mem",
            "BU (senza s)\nTime | Mem",
            "Space Eff.\nTime | Mem",
            "Top Down\nTime | Mem",
            "BU (Pareto)\nTime | Mem",
            "Space (Pareto)\nTime | Mem",
        ]

        table_data = []
        for sc in scenarios:
            sub = df[df["scenario"] == sc]
            first = sub.iloc[0]
            row = [
                sc.replace("scenario_", "sc_"),
                str(int(first["N"])),
                str(int(first["B"])),
                str(int(first["P"])),
            ]
            for algo_full in algo_abbr.keys():
                algo_row = sub[sub["algorithm"] == algo_full]
                if not algo_row.empty:
                    t = algo_row.iloc[0]["time_ms"]
                    m = algo_row.iloc[0]["memory_kib"]
                    t_str = f"{t:.2f} ms" if t >= 1.0 else f"{t:.3f} ms"
                    m_str = f"{m:.1f} KiB" if m >= 1.0 else f"{m:.2f} KiB"
                    row.append(f"{t_str}\n{m_str}")
                else:
                    row.append("-")
            table_data.append(row)

        fig, ax = plt.subplots(figsize=(16, 8))
        ax.axis("off")
        ax.set_title(
            "Tabella Comparativa Prestazioni Algoritmi (Tempo & Memoria RAM)",
            fontsize=14,
            weight="bold",
            pad=20,
        )

        table = ax.table(
            cellText=table_data,
            colLabels=col_labels,
            cellLoc="center",
            loc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.0, 2.0)

        # Stile testata e celle
        for (r, c), cell in table.get_celld().items():
            if r == 0:
                cell.set_facecolor("#2c3e50")
                cell.get_text().set_color("white")
            elif r % 2 == 0:
                cell.set_facecolor("#f8f9fa")

        plt.tight_layout()
        save_path = self.output_dir / "table_algorithms_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        if self.show_plots:
            plt.show()
        plt.close(fig)
        return save_path

    # Genera tutti i grafici e la tabella
    def plot_all(self):
        p1 = self.plot_optimal_value_comparison()
        p2 = self.plot_reconstruction_comparison()
        p3 = self.plot_pareto_impact()
        p4 = self.plot_comparison_table()
        return [p1, p2, p3, p4]
