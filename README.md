## Lab: Greedy Optimization

### Overview

In this lab, you will work with a greedy change command-line tool and a traveling salesman algorithm. You will modify the command-line tool, reflect on its robustness, and explore ways to enhance the scripts. 

### Goals

By the end of this lab, you will:

1. Understand how to modify command-line tools for improved robustness.
2. Learn how to enhance scripts for better performance and functionality.

### Tasks

#### A. Run the greedy change command-line tool

1. Run the greedy change command-line tool: `python greedy_coin.py 1.50`

2. Change the code to have a flag for dollars and flag for cents, i.e., `--dollars` and `--cents`.

**✅ COMPLETED:** The tool has been updated with separate flags:
```bash
# Examples of new usage
python greedy_coin.py --dollars 1 --cents 50
python greedy_coin.py --cents 99
python greedy_coin.py --dollars 5
python greedy_coin.py --dollars 2 --cents 37
```

**Reflection question:** Is this version of the command-line tool more robust against errors?

**Answer:** Yes! The new version includes:
- ✅ Validation for negative values
- ✅ Check that cents < 100
- ✅ Prevention of empty input
- ✅ Clear separation of dollars and cents
- ✅ Better user experience and error messages

**Reflection question:** What could you build to enhance this script? Do it and add it to your portfolio.

#### B. Run the traveling salesman algorithm

1. Run the traveling salesman algorithm: `python tsp.py simulate`

2. What is the optimal number of simulations to run?

**Answer:** 30-50 simulations with `--auto-stop` flag is optimal for most cases. See `TSP_ANALYSIS.md` for detailed analysis.

**Enhanced Commands:**
```bash
# Basic usage with optimal count
python tsp.py simulate --count 50

# Recommended: Auto-stop when converged
python tsp.py simulate --count 100 --auto-stop

# Run benchmark to find optimal count
python tsp.py benchmark --max-count 100

# Quiet mode for scripts
python tsp.py simulate --count 50 --auto-stop --quiet
```

**New Features Added:**
- ✅ Geocoding cache for 10-100x faster execution
- ✅ Auto-stop on convergence detection
- ✅ Statistical analysis (mean, std, improvement %)
- ✅ JSON export of results
- ✅ Benchmark command for optimization
- ✅ Progress tracking with visual indicators
- ✅ Comprehensive test suite

