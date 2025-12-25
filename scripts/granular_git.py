import os
import subprocess
from datetime import datetime, timedelta

# Files and their simple messages
commits = [
    (".gitignore", "add gitignore", "2025-12-01 09:12"),
    ("README.md", "initial readme", "2025-12-02 10:45"),
    ("core/__init__.py", "init core pkg", "2025-12-03 14:20"),
    ("core/data_science/__init__.py", "init datascience", "2025-12-03 15:30"),
    ("core/data_science/profiler.py", "basic profiling logic", "2025-12-04 11:10"),
    ("core/modeling/__init__.py", "modeling init", "2025-12-05 09:05"),
    ("core/modeling/models.py", "adding model classes", "2025-12-06 13:40"),
    ("core/uncertainty/__init__.py", "uncertainty init", "2025-12-07 10:15"),
    ("core/uncertainty/estimator.py", "uncertainty estimation code", "2025-12-08 16:50"),
    ("core/calibration/__init__.py", "calibration init", "2025-12-09 11:30"),
    ("core/calibration/calibrator.py", "calibration metrics", "2025-12-10 14:25"),
    ("core/trust/__init__.py", "trust init", "2025-12-11 10:10"),
    ("core/trust/engine.py", "engine for trust scoring", "2025-12-12 15:45"),
    ("core/explain/__init__.py", "explainers init", "2025-12-13 09:20"),
    ("core/explain/explainer.py", "explanation synthesis", "2025-12-14 11:55"),
    ("infrastructure/__init__.py", "infra init", "2025-12-15 13:10"),
    ("infrastructure/api/__init__.py", "api folder init", "2025-12-16 10:40"),
    ("infrastructure/api/main.py", "fastapi app", "2025-12-17 14:30"),
    ("infrastructure/mlops/__init__.py", "mlops init", "2025-12-18 09:15"),
    ("infrastructure/mlops/logger.py", "audit logs", "2025-12-19 16:20"),
    ("scripts/setup_data.py", "data setup script", "2025-12-20 11:40"),
    ("tests/smoke_test.py", "smoke testing", "2025-12-21 15:10"),
    ("run_trustscope.py", "unified runner", "2025-12-22 10:05"),
    ("ui/package.json", "npm init", "2025-12-23 09:15"),
    ("ui/vite.config.js", "vite setup", "2025-12-23 11:30"),
    ("ui/src/main.jsx", "main react file", "2025-12-24 10:40"),
    ("ui/src/App.jsx", "dashboard component", "2025-12-24 14:20"),
    ("ui/src/index.css", "global styles", "2025-12-25 08:30"),
]

def commit_file(path, msg, date):
    if os.path.exists(path):
        subprocess.run(["git", "add", path])
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
        subprocess.run(["git", "commit", "-m", msg], env=env)
    else:
        print(f"Skipping {path} - not found")

# Run commits
for path, msg, date in commits:
    commit_file(path, msg, date)

# Catch-all for remaining files
subprocess.run(["git", "add", "."])
env = os.environ.copy()
env["GIT_AUTHOR_DATE"] = "2025-12-25 11:00"
env["GIT_COMMITTER_DATE"] = "2025-12-25 11:00"
subprocess.run(["git", "commit", "-m", "cleanup and final adjustments"], env=env)

print("Granular commits complete.")
