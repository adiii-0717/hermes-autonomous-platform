#!/usr/bin/env python3
import sys
import time
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def main():
    print('=' * 60)
    print('HERMES DEV STUDIO — FULL SYSTEM TEST SUITE RUNNER')
    print('=' * 60)
    
    loader = unittest.TestLoader()
    tests_dir = project_root / 'tests'
    suite = loader.discover(start_dir=str(tests_dir), pattern='test_*.py')
    
    total_discovered = suite.countTestCases()
    print(f'[*] Discovered {total_discovered} test cases in {tests_dir}')
    print('[*] Executing full test suite...')
    print()
    
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    elapsed = time.time() - start_time
    
    passed = total_discovered - len(result.failures) - len(result.errors) - len(result.skipped)
    
    print()
    print('=' * 60)
    print('FULL TEST SUITE EXECUTION SUMMARY')
    print('=' * 60)
    print(f'Total Discovered : {total_discovered}')
    print(f'Passed           : {passed}')
    print(f'Failed           : {len(result.failures)}')
    print(f'Errors           : {len(result.errors)}')
    print(f'Skipped          : {len(result.skipped)}')
    print(f'Total Duration   : {elapsed:.2f} seconds')
    print('=' * 60)
    
    if result.wasSuccessful():
        print('SUCCESS: ALL DISCOVERED TESTS PASSED CLEANLY!')
        sys.exit(0)
    else:
        print('FAILURE: TEST SUITE CONTAINED FAILURES OR ERRORS.')
        sys.exit(1)

if __name__ == '__main__':
    main()