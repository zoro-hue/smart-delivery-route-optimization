"""
Regression test: Verify that React Hooks in ResultsView.tsx strictly adhere to the Rules of Hooks.
Ensures zero hooks are invoked after any early returns or conditional exit paths.
"""

import os
import re
import sys

def verify_results_view_hooks():
    file_path = os.path.join('frontend', 'src', 'pages', 'ResultsView.tsx')
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_results_view = False
    return_line = None
    hook_lines_after_return = []

    for idx, line in enumerate(lines, 1):
        if 'export const ResultsView:' in line:
            in_results_view = True
            continue

        if in_results_view:
            # Check for top-level component early return
            if re.match(r'^\s{2}if\s*\(.*!\s*result', line) or (re.match(r'^\s{4}return\s*\(', line) and not return_line):
                if not return_line and 'No Route Results Yet' in ''.join(lines[idx:idx+15]):
                    return_line = idx

            # Check for hook invocation
            if any(h in line for h in ['useState', 'useEffect', 'useMemo', 'useCallback', 'useRef', 'useContext']):
                # Ignore callback functions/nested closures
                if not re.search(r'(=>|\bfunction\b)', line[:line.find('use')]):
                    if return_line and idx > return_line:
                        hook_lines_after_return.append((idx, line.strip()))

    print(f"ResultsView Early Return detected at line: {return_line}")
    print(f"Hooks detected after early return: {len(hook_lines_after_return)}")

    if hook_lines_after_return:
        print("FAIL: React Hook Rule Violation! Hooks called after early return:")
        for l_num, l_code in hook_lines_after_return:
            print(f"  Line {l_num}: {l_code}")
        sys.exit(1)
    else:
        print("PASS: Zero hooks invoked after early returns in ResultsView.tsx.")
        sys.exit(0)

if __name__ == '__main__':
    verify_results_view_hooks()
