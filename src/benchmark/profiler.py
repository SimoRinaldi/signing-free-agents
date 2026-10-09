import time
import tracemalloc
from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkResult:
    result: Any
    time_ms: float
    peak_memory_kib: float

    @property
    def value(self):
        return self.result[0] if isinstance(self.result, tuple) else self.result

    def __iter__(self):
        return iter((self.value, self.time_ms, self.peak_memory_kib))


# Classe per la profilazione delle prestazioni di tempo e memoria RAM
class PerformanceProfiler:
    def __init__(self, repetitions: int = 10):
        self.repetitions = repetitions

    # Misura il tempo minimo di esecuzione su n ripetizioni
    def measure_time(self, func, *args, **kwargs):
        times = []
        result = None

        for i in range(self.repetitions):
            start = time.perf_counter()
            current_result = func(*args, **kwargs)
            end = time.perf_counter()

            times.append((end - start) * 1000)
            if i == 0:
                result = current_result

        min_time_ms = min(times)
        return result, min_time_ms

    # Misura il picco di memoria RAM allocata con tracemalloc
    def measure_peak_memory(self, func, *args, **kwargs):
        tracemalloc.start()
        tracemalloc.reset_peak()

        result = func(*args, **kwargs)

        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_kib = peak_bytes / 1024
        return result, peak_kib

    # Esegue entrambe le misurazioni e restituisce un BenchmarkResult
    def profile(self, func, *args, **kwargs) -> BenchmarkResult:
        result, time_ms = self.measure_time(func, *args, **kwargs)
        _, peak_kib = self.measure_peak_memory(func, *args, **kwargs)
        return BenchmarkResult(result=result, time_ms=time_ms, peak_memory_kib=peak_kib)
