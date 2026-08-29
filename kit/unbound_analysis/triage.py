import sys

def summarize_results(filepath):
    files = {}
    with open(filepath) as f:
        current_file = None
        for line in f:
            if line.startswith('\n') or not line.strip():
                continue
            if not line.startswith(' '):
                current_file = line.strip()
                files[current_file] = []
            else:
                files[current_file].append(line.strip())
                
    # Sort files by number of unbound variables found
    sorted_files = sorted(files.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"Total files with potential issues: {len(sorted_files)}")
    print(f"Total unbound variables found: {sum(len(v) for v in files.values())}\n")
    
    print("Top files by number of unbound variables:")
    for f, vars in sorted_files[:10]:
        print(f"  - {f}: {len(vars)} unbound variables")
        
    # Look for specific high-risk patterns
    print("\nNotable findings (high usage count):")
    for f, vars in files.items():
        for v in vars:
            # parsing something like: "- pari (imported line 162): used 12 time(s) (e.g. lines [754, 756, 4247])"
            try:
                count_str = v.split('used ')[1].split(' time')[0]
                count = int(count_str)
                if count > 5:
                    print(f"  - {f}: {v}")
            except Exception:
                pass

if __name__ == '__main__':
    summarize_results('unbound_results_v2.txt')
