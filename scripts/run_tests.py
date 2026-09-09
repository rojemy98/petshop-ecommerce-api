import subprocess
import sys


def main():
    print("=" * 60)
    print("PETSHOP E-COMMERCE - AUTOMATED TEST REPORT")
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-v",
            "--cov=services",
            "--cov-report=term-missing"
        ]
    )

    print("\n" + "=" * 60)

    if result.returncode == 0:
        print("RESULT: ALL TESTS PASSED")
    else:
        print("RESULT: SOME TESTS FAILED")

    print("=" * 60)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()