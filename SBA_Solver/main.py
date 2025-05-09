# Add parent folder to allow import of shared modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import json
import os
import logging
import sba_solver
from Shared.sigma_report import SigmaReportParams

# SBA Solver parameters
# The ID of the base liability cash flow projection
base_projection_id = 59776

# List of the pivot points at which you want to run the solver. It will solve for BEL at ech of these time points in the above projection
solver_time_points = [0]
# solver_time_points = [0, 12, 24, 36, 48, 60, 120, 240]


def setup_logging():
    # Change this to appropriate level for your run
    logging_level = logging.INFO

    # Setup Logger
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

def get_reports_data() -> dict[str, SigmaReportParams]:
    # Load reports.json from the local directory
    current_dir = os.path.dirname(__file__)
    reports_file_path = os.path.join(current_dir, 'reports.json')

    with open(reports_file_path, 'r') as file:
        reports_json = json.load(file)

    # Convert each value in reports_data to a SigmaReportParams object
    reports_data = {key: SigmaReportParams.from_dict(value) for key, value in reports_json.items()}

    return reports_data

def run():
    setup_logging()
    reports = get_reports_data()
    solver = sba_solver.SbaSolver(base_projection_id, reports)

    solver.calculate_bel(solver_time_points)
    solver.print_results()


if __name__ == "__main__":
    run()
