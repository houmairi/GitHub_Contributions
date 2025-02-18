# Git Repository Contribution Analyzer

A Python script that provides detailed analysis of developer contributions in Git repositories. This tool offers comprehensive insights into coding patterns, impact metrics, and developer activity.

## Features

- Detailed contribution analysis per developer
- Flexible date range filtering
- Developer identity mapping (combine multiple usernames)
- Three categories of metrics:
  1. Basic Metrics
     - Commit counts and percentages
     - Files changed
     - Lines added/deleted
     - Net line changes
  2. Impact Metrics
     - Average files per commit
     - Average lines per commit
     - Code churn tracking
     - Impact ratio (net changes vs. total changes)
  3. Activity Metrics
     - Active days count
     - Commits per active day
     - Peak activity hours

## Requirements

- Python 3.x
- GitPython package

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/houmairi/GitHub_Contributions
   cd GitHub_Contributions
   ```

2. Install required package:
   ```bash
   pip install gitpython
   ```

## Usage

Basic usage:
```bash
python main.py /path/to/repository
```

Analyze specific date range:
```bash
python main.py /path/to/repository --start-date 2024-01-01 --end-date 2024-02-19
```

### Example Output

```
Developer Contribution Analysis
==================================================

Developer: ExampleDev
------------------------------
Basic Metrics:
  Total commits:     310 (73.5% of all commits)
  Files changed:     1052
  Lines added:       40001
  Lines deleted:     17253
  Net lines:         22748

Impact Metrics:
  Avg files/commit:  3.4
  Avg lines/commit:  184.7
  Code churn:        57254 lines
  Impact ratio:      0.40

Activity Metrics:
  Active days:       45
  Commits/active day: 6.9
  Peak commit hour:  14:00
```

## Customization

You can modify the developer identity mappings in the script by editing the `AUTHOR_MAPPINGS` dictionary:

```python
AUTHOR_MAPPINGS = {
    'alternate_username': 'main_username',
    'another_alias': 'main_username'
}
```

## Understanding the Metrics

### Basic Metrics
- **Commit percentage**: Shows the developer's share of total project commits
- **Files changed**: Total number of file modifications
- **Lines added/deleted**: Raw code changes
- **Net lines**: Overall code growth (additions - deletions)

### Impact Metrics
- **Average files per commit**: Indicates commit scope/size
- **Average lines per commit**: Shows typical commit impact
- **Code churn**: Total lines modified (additions + deletions)
- **Impact ratio**: Measures net change vs. total modifications (-1 to 1)

### Activity Metrics
- **Active days**: Days with at least one commit
- **Commits per active day**: Activity intensity
- **Peak commit hour**: Most common commit time

## Contributing

Feel free to submit issues and enhancement requests!