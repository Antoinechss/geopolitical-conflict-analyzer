import sys
import subprocess

OLLAMA_MODEL = "mistral:instruct"


def main():
    input_text = sys.stdin.read().strip()

    if not input_text:
        sys.exit(0)

    result = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL],
        input=input_text,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(1)

    # IMPORTANT: stdout only, no prints
    print(result.stdout.strip())


if __name__ == "__main__":
    main()
