# ...existing code...
#!/usr/bin/env python3
"""
Parse partial_results.txt and plot:
 - batch uncertainty (Incerteza Média Batch)
 - test R2
 - test MAE
over iterations.
Usage:
    python3 print_partial_res.py partial_results.txt --out partial_results.png
"""
import re
import sys
import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ITER_RE = re.compile(
    r"Itera(?:ção|cao)\s+(\d+):.*?Incerteza Média Batch:\s*([\-0-9\.eE]+)\s*\|\s*Test R2:\s*([\-0-9\.eE]+)\s*\|\s*Test MAE:\s*([\-0-9\.eE]+)",
    re.IGNORECASE,
)
START_RE = re.compile(r"Start:.*Test R2=([\-0-9\.eE]+)\s*\|\s*Test MAE=([\-0-9\.eE]+)")

def parse_file(path):
    iterations = []
    batch_unc = []
    r2 = []
    mae = []
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            m = ITER_RE.search(line)
            if m:
                it = int(m.group(1))
                iterations.append(it)
                batch_unc.append(float(m.group(2)))
                r2.append(float(m.group(3)))
                mae.append(float(m.group(4)))
                continue
            m2 = START_RE.search(line)
            if m2 and 0 not in iterations:
                # Treat start as iteration 0
                iterations.insert(0, 0)
                batch_unc.insert(0, float('nan'))
                r2.insert(0, float(m2.group(1)))
                mae.insert(0, float(m2.group(2)))
    if not iterations:
        raise ValueError("No iteration lines found. Check file format.")
    df = pd.DataFrame({
        'iteration': iterations,
        'batch_uncertainty': batch_unc,
        'test_r2': r2,
        'test_mae': mae,
    })
    df = df.sort_values('iteration').reset_index(drop=True)
    return df

def plot_df(df, out_path=None, show=True):
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle('Active Learning (QBC) Partial Results Over Iterations')
    axes[0].plot(df['iteration'], df['batch_uncertainty'], marker='.', lw=0.8, color='C0')
    axes[0].set_ylabel('Batch uncertainty')
    axes[0].grid(True)

    axes[1].plot(df['iteration'], df['test_r2'], marker='.', lw=0.8, color='C1')
    axes[1].set_ylabel('Test R2')
    # axes[1].set_ylim(-10, 2.05)
    axes[1].grid(True)

    axes[2].plot(df['iteration'], df['test_mae'], marker='.', lw=0.8, color='C2')
    axes[2].set_ylabel('Test MAE')
    axes[2].set_xlabel('Iteration')
    axes[2].grid(True)

    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=150)
        print(f"Saved figure to: {out_path}")
    if show:
        plt.show()
    plt.close(fig)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('file', nargs='?', default='partial_results.txt', help='partial results file')
    p.add_argument('--out', '-o', default='partial_results.png', help='output image file')
    args = p.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    df = parse_file(path)
    print(df.head())
    plot_df(df, out_path=args.out, show=True)

if __name__ == '__main__':
    main()
# ...existing code...