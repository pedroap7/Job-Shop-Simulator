import threading
import json

class BatchRunner:
    """Utility to run several experiment specs sequentially.

    Each spec should be a dict with keys:
      - "heuristic": "sa" or "ga" (or full class import path)
      - "params": dict of parameters for the heuristic
      - "mode": "iterations" or "time"
      - "limit": numeric limit
      - "name": optional experiment name

    The runner calls the provided factory `get_heuristic_callable(spec)` to
    obtain an object with a `.run(...)` / `.run_with_time_limit(...)` interface.
    Results are yielded to `on_result(result)` after each experiment.
    """

    def __init__(self, get_heuristic_callable, on_result=None, on_error=None):
        self.get_heuristic = get_heuristic_callable
        self.on_result = on_result
        self.on_error = on_error
        self._thread = None
        self._stop = False

    def run_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            specs = json.load(f)
        self.run_specs(specs)

    def run_specs(self, specs):
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Batch is already running")
        self._stop = False
        self._thread = threading.Thread(target=self._run_thread, args=(specs,))
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._stop = True
        if self._thread:
            self._thread.join(timeout=0.1)

    def _run_thread(self, specs):
        for spec in specs:
            if self._stop:
                break
            try:
                heuristic = self.get_heuristic(spec)
                mode = spec.get('mode', 'iterations')
                limit = spec.get('limit', 1000)
                name = spec.get('name') or f"Exp_{len(spec)}"

                if mode == 'iterations':
                    results = heuristic.run(max_iterations=int(limit))
                else:
                    results = heuristic.run_with_time_limit(time_limit_seconds=float(limit))

                results['name'] = name
                if self.on_result:
                    self.on_result(results)
            except Exception as e:
                if self.on_error:
                    self.on_error(e)
                else:
                    raise
