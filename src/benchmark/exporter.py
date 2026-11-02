import csv
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from src.core.models import BenchmarkMetric


class DataExporter:
    def __init__(self, output_dir: Union[str, Path] = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_records: List[Dict[str, Any]] = []

    def add_metric(self, record: Union[Dict[str, Any], BenchmarkMetric]) -> None:
        if isinstance(record, BenchmarkMetric):
            self.metrics_records.append(record.to_dict())
        else:
            self.metrics_records.append(record)

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

    def export_matrix_to_csv(
        self,
        matrix: List[List[Any]],
        filename: str,
        row_labels: Optional[List[str]] = None,
        col_labels: Optional[List[str]] = None,
    ) -> Path:
        file_path = self.output_dir / filename
        num_cols = len(matrix[0]) if matrix else 0

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

    @staticmethod
    def _visible_len(s: Any) -> int:
        return len(re.sub(r"\x1b\[[0-9;]*m", "", str(s)))

    @classmethod
    def _pad_cell(cls, val: Any, width: int, align: str) -> str:
        s = str(val)
        vlen = cls._visible_len(s)
        pad = max(0, width - vlen)
        if align == "right":
            return (" " * pad) + s
        elif align == "center":
            left_pad = pad // 2
            right_pad = pad - left_pad
            return (" " * left_pad) + s + (" " * right_pad)
        else:
            return s + (" " * pad)

    @classmethod
    def format_box_table(
        cls,
        headers: List[str],
        rows: List[List[Any]],
        alignments: Optional[List[str]] = None,
    ) -> str:
        """Formatta una tabella con bordi Unicode a griglia chiusa (box-drawing)."""
        num_cols = len(headers)
        if not alignments:
            alignments = ["left"] * num_cols

        col_widths = [cls._visible_len(h) for h in headers]
        for r in rows:
            for idx, val in enumerate(r):
                col_widths[idx] = max(col_widths[idx], cls._visible_len(val))

        top_line = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        header_sep = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        def format_row(vals):
            cells = []
            for val, w, align in zip(vals, col_widths, alignments):
                cells.append(f" {cls._pad_cell(val, w, align)} ")
            return "│" + "│".join(cells) + "│"

        lines = [top_line, format_row(headers), header_sep]
        for r in rows:
            lines.append(format_row(r))
        lines.append(bottom_line)
        return "\n".join(lines)

    def format_matrix(
        self,
        matrix: List[List[Any]],
        row_labels: Optional[List[str]] = None,
        col_labels: Optional[List[str]] = None,
        highlight_cell: Optional[Tuple[int, int]] = None,
    ) -> str:
        """Formatta una matrice numerica in una tabella a griglia chiusa con bordi Unicode."""
        if not matrix:
            return ""

        num_cols = len(matrix[0])
        if col_labels is None:
            col_labels = [f"b={b}" for b in range(num_cols)]

        headers = ["Ruolo / Budget"] + col_labels
        rows_data = []

        for i, row in enumerate(matrix):
            label = row_labels[i] if row_labels and i < len(row_labels) else f"i={i}"
            formatted_vals = []
            for j, val in enumerate(row):
                base_str = f"{val:.1f}" if isinstance(val, float) else str(val)
                if highlight_cell and highlight_cell == (i, j):
                    base_str = f"\033[1;32m★ {base_str}\033[0m"
                formatted_vals.append(base_str)
            rows_data.append([label] + formatted_vals)

        alignments = ["left"] + ["right"] * num_cols
        return self.format_box_table(headers, rows_data, alignments)
