"""
run_project.py
Master runner for the Customer Lifecycle and Revenue Intelligence System.
Provides a unified entrypoint to execute summary reports, rebuild the database,
run SQL analytics, or launch the interactive web dashboard.
"""
import sys
import os
import subprocess

def show_banner():
    print("=" * 80)
    print("  CUSTOMER LIFECYCLE AND REVENUE INTELLIGENCE SYSTEM")
    print("  Unified Project Runner")
    print("=" * 80)
    print()

def check_database():
    db_path = "retail_analytics.db"
    if not os.path.exists(db_path) or os.path.getsize(db_path) < 1000:
        print("⚠️  SQLite database (retail_analytics.db) is not built yet or is an LFS placeholder.")
        print("   Auto-building database from data/*.csv...")
        subprocess.run([sys.executable, "build_database.py"], check=True)
    else:
        print("✅ SQLite database (retail_analytics.db) is ready.")

def run_summary():
    print("\n🚀 Running Executive Summary Report...")
    subprocess.run([sys.executable, "run_summary.py"], check=True)

def launch_dashboard():
    print("\n🌐 Launching Interactive Web Dashboard (Streamlit)...")
    print("   Open your browser at: http://localhost:8501")
    subprocess.run(["streamlit", "run", "app.py"])

def rebuild_database():
    print("\n🔨 Rebuilding retail_analytics.db...")
    subprocess.run([sys.executable, "build_database.py"], check=True)

def main():
    show_banner()
    check_database()

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--summary", "-s", "summary"]:
            run_summary()
            return
        elif arg in ["--web", "-w", "web", "dashboard", "streamlit"]:
            launch_dashboard()
            return
        elif arg in ["--build", "-b", "build", "db"]:
            rebuild_database()
            return

    # Default execution: run summary and show available commands
    run_summary()

    print("\n💡 Available commands:")
    print("   python run_project.py --summary    : Display terminal summary report")
    print("   python run_project.py --web        : Launch interactive Streamlit web dashboard")
    print("   python run_project.py --build      : Rebuild & index SQLite database")
    print()

if __name__ == "__main__":
    main()

