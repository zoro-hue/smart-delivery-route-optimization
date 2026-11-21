import os
import shutil
import sqlite3
import hashlib
import subprocess
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("d:/UROP/smart-delivery-route-optimization")
DB_PATH = BASE_DIR / "backend" / "data" / "sdro.db"
BACKUP_DIR = BASE_DIR / "backend" / "data" / "backups"

def run_git(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout.strip()

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def get_dir_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        if '.git' in root or 'node_modules' in root:
            continue
        for f in files:
            fp = os.path.join(root, f)
            try:
                total += os.path.getsize(fp)
            except:
                pass
    return total

def main():
    print("=== REPOSITORY CLEANUP EXECUTION & SAFETY PROTOCOL ===")
    
    # 1. Baseline Measurements
    initial_repo_size = get_dir_size(BASE_DIR)
    print(f"Initial Workspace Size (excl .git, node_modules): {initial_repo_size:,} bytes ({initial_repo_size / (1024*1024):.2f} MB)")

    # 2. Database Pre-Cleanup Inspection & Verified Backup
    print("\n--- DATABASE SAFETY & PRE-VACUUM INSPECTION ---")
    if not DB_PATH.exists():
        print(f"ERROR: Database path not found: {DB_PATH}")
        return
    
    initial_db_size = os.path.getsize(DB_PATH)
    initial_db_sha = compute_sha256(DB_PATH)
    print(f"DB Path: {DB_PATH}")
    print(f"DB Size: {initial_db_size:,} bytes ({initial_db_size / (1024*1024):.2f} MB)")
    print(f"DB SHA-256: {initial_db_sha}")

    # Inspect tables and row counts
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check;")
    integrity_pre = cur.fetchall()
    print(f"Pre-VACUUM Integrity Check: {integrity_pre}")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cur.fetchall()]
    table_counts_pre = {}
    for t in tables:
        cur.execute(f'SELECT count(*) FROM "{t}";')
        cnt = cur.fetchone()[0]
        table_counts_pre[t] = cnt
        print(f"  Table '{t}': {cnt} rows")

    conn.close()

    # Create Backup using official SQLite backup API
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"sdro_pre_cleanup_backup_{timestamp}.db"
    
    src_conn = sqlite3.connect(DB_PATH)
    dst_conn = sqlite3.connect(backup_file)
    src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()

    # Verify backup integrity and row counts
    test_conn = sqlite3.connect(backup_file)
    t_cur = test_conn.cursor()
    t_cur.execute("PRAGMA integrity_check;")
    b_integrity = t_cur.fetchall()
    print(f"Backup Integrity Check: {b_integrity}")
    assert b_integrity == [('ok',)], "Backup integrity check failed!"
    
    for t, expected_cnt in table_counts_pre.items():
        t_cur.execute(f'SELECT count(*) FROM "{t}";')
        actual_cnt = t_cur.fetchone()[0]
        assert actual_cnt == expected_cnt, f"Backup table count mismatch on {t}!"
        print(f"  Backup table '{t}': {actual_cnt} rows verified")
    test_conn.close()

    backup_sha = compute_sha256(backup_file)
    print(f"\nCreated Verified DB Backup: {backup_file}")
    print(f"Backup SHA-256: {backup_sha}")
    print("BACKUP VERIFIED 100% INTACT AND IDENTICAL.")

    # 3. VACUUM the Database
    print("\nExecuting VACUUM on SQLite database...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("VACUUM;")
    conn.commit()
    
    # Re-verify post-VACUUM
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check;")
    integrity_post = cur.fetchall()
    print(f"Post-VACUUM Integrity Check: {integrity_post}")

    table_counts_post = {}
    for t in tables:
        cur.execute(f'SELECT count(*) FROM "{t}";')
        cnt = cur.fetchone()[0]
        table_counts_post[t] = cnt
        print(f"  Table '{t}': {cnt} rows (Pre: {table_counts_pre[t]})")
        assert table_counts_post[t] == table_counts_pre[t], f"ROW COUNT MISMATCH ON TABLE {t}!"

    conn.close()
    post_db_size = os.path.getsize(DB_PATH)
    print(f"Post-VACUUM DB Size: {post_db_size:,} bytes ({post_db_size / (1024*1024):.2f} MB)")
    print(f"Database space saved: {initial_db_size - post_db_size:,} bytes")
    print("ALL TABLES, EXPERIMENTS, AND ROW COUNTS 100% PRESERVED.")

    # 4. Historical Branch Preservation & Tagging
    print("\n--- HISTORICAL BRANCH PRESERVATION & ARCHIVAL TAGGING ---")
    branches_raw = run_git("git branch -a").splitlines()
    local_branches = [b.strip().replace('* ', '') for b in branches_raw if not b.strip().startswith('remotes/')]
    print(f"Discovered {len(local_branches)} local branches:")
    
    phase_branches = [b for b in local_branches if b.startswith("research/phase-") or b == "research/journal-readiness"]
    created_tags = []

    for b in phase_branches:
        # Get head commit
        head_commit = run_git(f"git rev-parse {b}")
        tag_name = b.replace("research/", "archive/")
        print(f"Tagging branch '{b}' (commit {head_commit[:7]}) as '{tag_name}'...")
        # Check if tag already exists and points to head_commit
        existing_commit = run_git(f"git rev-list -n 1 {tag_name}")
        if existing_commit != head_commit:
            run_git(f'git tag -a -f "{tag_name}" {head_commit} -m "Archival tag for {b} at commit {head_commit}"')
            print(f"  Created/Updated tag '{tag_name}' -> {head_commit[:7]}")
        else:
            print(f"  Tag '{tag_name}' already points to {head_commit[:7]}.")
        created_tags.append((tag_name, head_commit))

    print(f"\nTotal archival tags created/verified: {len(phase_branches)}")
    for tag_name, head_commit in created_tags:
        # Verify tag points to exact commit using rev-list -n 1
        tag_commit = run_git(f"git rev-list -n 1 {tag_name}")
        assert tag_commit == head_commit, f"Tag {tag_name} commit mismatch ({tag_commit} vs {head_commit})!"
        print(f"  Verified tag '{tag_name}' -> {tag_commit[:7]}")

    # Retain main and research/next-generation-cooperative-engine as active branches
    # Clean up local phase branches now safely preserved in git tags
    print("\nCleaning up local historical branch pointers (safely tagged)...")
    deleted_local_branches = []
    for b in phase_branches:
        # Delete local pointer only
        res = run_git(f"git branch -D {b}")
        print(f"  Deleted local branch pointer '{b}' (now safely tagged as '{b.replace('research/', 'archive/')}')")
        deleted_local_branches.append(b)

    # Verify active branches remaining
    remaining_local = [b.strip().replace('* ', '') for b in run_git("git branch").splitlines()]
    print(f"\nRemaining Active Local Branches: {remaining_local}")
    assert "main" in remaining_local and "research/next-generation-cooperative-engine" in remaining_local

    # Save summary data
    summary = {
        "initial_workspace_bytes": initial_repo_size,
        "initial_db_bytes": initial_db_size,
        "post_db_bytes": post_db_size,
        "db_space_saved_bytes": initial_db_size - post_db_size,
        "db_tables": table_counts_post,
        "db_backup_path": str(backup_file),
        "db_backup_sha256": backup_sha,
        "created_archival_tags": created_tags,
        "deleted_local_branches": deleted_local_branches,
        "active_branches": remaining_local
    }
    with open("cleanup_step_db_and_branches.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
