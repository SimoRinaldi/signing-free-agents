import csv
from pathlib import Path
from typing import Any, Dict, List, Optional


# Classe responsabile dell'esportazione delle metriche e delle matrici di ispezione
class DataExporter:
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_records: List[Dict[str, Any]] = []

    # Registra una riga di metriche prestazionali
    def add_metric(self, record: Dict[str, Any]):
        self.metrics_records.append(record)

    # Esporta l'elenco delle metriche registrate su file CSV
    def export_metrics_to_csv(
        self, filename: str = "benchmark_metrics.csv"
    ) -> Optional[Path]:
        if not self.metrics_records:
            return None

        file_path = self.output_dir / filename
        fieldnames = list(self.metrics_records[0].keys())

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.metrics_records)

        return file_path

    # Esporta una matrice (m o s) su file CSV con etichette di riga e colonna
    def export_matrix_to_csv(
        self,
        matrix: List[List[Any]],
        filename: str,
        row_labels: Optional[List[str]] = None,
        col_labels: Optional[List[str]] = None,
    ) -> Path:
        file_path = self.output_dir / filename
        num_rows = len(matrix)
        num_cols = len(matrix[0])

        if col_labels is None:
            col_labels = [f"b={b}" for b in range(num_cols)]

        header = ["Ruolo / Stato"] + col_labels

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for i, row in enumerate(matrix):
                label = (
                    row_labels[i] if row_labels and i < len(row_labels) else f"i={i}"
                )
                formatted_row = [label] + [
                    f"{val:.1f}" if isinstance(val, float) else val for val in row
                ]
                writer.writerow(formatted_row)

        return file_path

    # Formattazione della matrice per ispezione con header, indentazione e 1 decimale
    def format_matrix(self, matrix, row_labels=None, col_labels=None):
        if not matrix:
            return ""

        num_cols = len(matrix[0])
        if col_labels is None:
            col_labels = [f"b={b}" for b in range(num_cols)]

        headers = ["Ruolo"] + col_labels
        rows_data = []

        for i, row in enumerate(matrix):
            label = row_labels[i] if row_labels and i < len(row_labels) else f"i={i}"
            formatted_vals = [
                f"{val:.1f}" if isinstance(val, float) else str(val) for val in row
            ]
            rows_data.append([label] + formatted_vals)

        col_widths = [len(h) for h in headers]
        for row in rows_data:
            for c_idx, cell in enumerate(row):
                col_widths[c_idx] = max(col_widths[c_idx], len(cell))

        def format_row(row):
            parts = [row[0].ljust(col_widths[0])]
            parts.extend(row[c].rjust(col_widths[c]) for c in range(1, len(row)))
            return "   ".join(parts)

        lines = [format_row(headers)]
        for row in rows_data:
            lines.append(format_row(row))

        return "\n".join(lines)
