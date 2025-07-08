import json
import os
from datetime import datetime
import numpy as np  # Needed to handle pandas/numpy data types

class AuditLogger:
    def __init__(self, log_file="audit_log.json"):
        self.log_file = log_file
        self.logs = []
        self.load_logs()

    def load_logs(self):
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    self.logs = json.load(f)
            else:
                self.logs = []
        except json.JSONDecodeError:
            print("⚠️ Corrupted audit_log.json — starting with an empty log.")
            self.logs = []

    def _convert_json_safe(self, item):
        """Convert numpy data types to native Python types"""
        def convert(val):
            if isinstance(val, (np.integer,)): return int(val)
            if isinstance(val, (np.floating,)): return float(val)
            if isinstance(val, (np.ndarray,)): return val.tolist()
            return val
        return {k: convert(v) for k, v in item.items()}

    def log(self, user, transaction_type, items):
        # Ensure all items are JSON-serializable
        cleaned_items = [self._convert_json_safe(item) for item in items]

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user,
            "transaction_type": transaction_type,
            "items": cleaned_items
        }

        self.logs.append(entry)

        with open(self.log_file, "w") as f:
            json.dump(self.logs, f, indent=2)

    def get_logs(self):
        return self.logs
