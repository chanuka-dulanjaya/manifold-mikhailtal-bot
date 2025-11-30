#!/usr/bin/env python3
"""
Verify Repository File Structure
Checks that all required files exist
"""
import os
from pathlib import Path

# Define expected file structure
REQUIRED_STRUCTURE = {
    'Root Files': [
        'README.md',
        'QUICKSTART.md',
        'INSTALL.md',
        'PROJECT_SUMMARY.md',
        'CONTRIBUTING.md',
        'WINDOWS_GUIDE.md',
        'VERSION_NOTES.md',
        'LICENSE',
        'requirements.txt',
        'setup.py',
        '.env.example',
        '.gitignore',
        'test_bot.py',
    ],
    'Source Files': [
        'src/__init__.py',
        'src/main.py',
        'src/config.py',
        'src/manifold_client.py',
        'src/ensemble.py',
        'src/risk_manager.py',
    ],
    'Strategy Files': [
        'src/strategies/__init__.py',
        'src/strategies/base_strategy.py',
        'src/strategies/llm_strategy.py',
        'src/strategies/momentum_strategy.py',
        'src/strategies/contrarian_strategy.py',
        'src/strategies/value_strategy.py',
        'src/strategies/sentiment_strategy.py',
    ],
    'Utility Files': [
        'src/utils/__init__.py',
    ],
    'Test Files': [
        'tests/test_strategies.py',
    ],
    'GitHub Actions': [
        '.github/workflows/ci.yml',
    ],
}

OPTIONAL_FILES = {
    'Data Directory': [
        'data/performance.json',
        'data/trades.json',
    ],
    'Notebooks': [
        'notebooks/',
    ],
}


def check_file(filepath: str, base_path: Path) -> bool:
    """Check if a file exists"""
    full_path = base_path / filepath
    
    # If it ends with '/', treat as directory
    if filepath.endswith('/'):
        return full_path.is_dir()
    
    return full_path.exists()


def verify_structure(base_path: Path = None):
    """Verify the repository structure"""
    
    if base_path is None:
        base_path = Path(__file__).parent
    
    print("=" * 70)
    print("Repository File Structure Verification")
    print("=" * 70)
    print(f"\nBase path: {base_path}\n")
    
    all_good = True
    missing_files = []
    
    # Check required files
    for category, files in REQUIRED_STRUCTURE.items():
        print(f"\n{category}:")
        print("-" * 70)
        
        for filepath in files:
            exists = check_file(filepath, base_path)
            status = "✓" if exists else "✗"
            
            if exists:
                print(f"  {status} {filepath}")
            else:
                print(f"  {status} {filepath} [MISSING]")
                all_good = False
                missing_files.append(filepath)
    
    # Check optional files
    print("\n\nOptional Files:")
    print("-" * 70)
    
    for category, files in OPTIONAL_FILES.items():
        print(f"\n{category}:")
        for filepath in files:
            exists = check_file(filepath, base_path)
            status = "✓" if exists else "-"
            print(f"  {status} {filepath}")
    
    # Summary
    print("\n" + "=" * 70)
    if all_good:
        print("✓ All required files present!")
    else:
        print(f"✗ Missing {len(missing_files)} required file(s):")
        for f in missing_files:
            print(f"  - {f}")
    print("=" * 70)
    
    # Create missing directories if needed
    if not all_good:
        print("\n" + "=" * 70)
        print("Creating Missing Files/Directories")
        print("=" * 70)
        
        # Create data directory
        data_dir = base_path / 'data'
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {data_dir}")
        
        # Create notebooks directory
        notebooks_dir = base_path / 'notebooks'
        if not notebooks_dir.exists():
            notebooks_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {notebooks_dir}")
        
        # Create empty performance.json
        perf_file = data_dir / 'performance.json'
        if not perf_file.exists():
            perf_file.write_text('{}')
            print(f"✓ Created: {perf_file}")
        
        # Create empty trades.json
        trades_file = data_dir / 'trades.json'
        if not trades_file.exists():
            trades_file.write_text('[]')
            print(f"✓ Created: {trades_file}")
    
    return all_good


def count_lines_of_code(base_path: Path = None):
    """Count lines of Python code"""
    
    if base_path is None:
        base_path = Path(__file__).parent
    
    print("\n" + "=" * 70)
    print("Lines of Code Statistics")
    print("=" * 70)
    
    total_lines = 0
    file_counts = {}
    
    for py_file in base_path.rglob('*.py'):
        # Skip venv and other non-source directories
        if any(part in py_file.parts for part in ['venv', '.venv', 'build', 'dist', '.git']):
            continue
        
        try:
            lines = len(py_file.read_text(encoding='utf-8').splitlines())
            total_lines += lines
            
            # Categorize
            if 'test' in py_file.name:
                category = 'Tests'
            elif 'strategies' in py_file.parts:
                category = 'Strategies'
            elif py_file.parent.name == 'src':
                category = 'Core'
            else:
                category = 'Other'
            
            if category not in file_counts:
                file_counts[category] = []
            
            file_counts[category].append((py_file.name, lines))
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    for category in sorted(file_counts.keys()):
        print(f"\n{category}:")
        for name, lines in sorted(file_counts[category]):
            print(f"  {name:30s} {lines:5d} lines")
    
    print("\n" + "-" * 70)
    print(f"Total Python Code: {total_lines:,} lines")
    print("=" * 70)


if __name__ == '__main__':
    import sys
    
    base_path = Path(__file__).parent
    
    # Verify structure
    all_good = verify_structure(base_path)
    
    # Count lines
    count_lines_of_code(base_path)
    
    # Exit code
    sys.exit(0 if all_good else 1)