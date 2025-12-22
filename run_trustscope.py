import subprocess
import sys
import os
import time

def run():
    print("🚀 Starting TRUSTSCOPE Platform...")
    
    # 1. Start Backend
    print("Starting FastAPI Backend on http://localhost:8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "infrastructure.api.main:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # 2. Wait a moment for backend
    time.sleep(2)
    
    # 3. Start Frontend
    print("Starting Vite Frontend on http://localhost:5173...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="ui",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    print("\n✅ TRUSTSCOPE is now running!")
    print("- Backend: http://localhost:8000")
    print("- Dashboard: http://localhost:5173")
    print("\nPress Ctrl+C to stop both services.\n")
    
    # Set non-blocking read
    import fcntl
    for p in [backend_proc, frontend_proc]:
        fd = p.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    try:
        while True:
            for p, name in [(backend_proc, "BACKEND"), (frontend_proc, "FRONTEND")]:
                try:
                    line = p.stdout.readline()
                    if line:
                        print(f"[{name}] {line.strip()}")
                except Exception:
                    pass
            
            if backend_proc.poll() is not None:
                break
            if frontend_proc.poll() is not None:
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping TRUSTSCOPE...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    run()
