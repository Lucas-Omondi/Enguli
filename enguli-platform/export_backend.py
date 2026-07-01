import os

# Root directory of the Django project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Target files inside the apps
TARGET_FILES = ['views.py', 'serializers.py', 'urls.py', 'admin.py', 'models.py', 'services.py']
SPECIFIC_FILES = [
    os.path.join('config', 'urls.py'),
    os.path.join('config', 'settings.py'),
    'requirements.txt'
]

OUTPUT_FILENAME = 'backend_complete_dump.txt'


def export_backend():
    print("Packing backend files for analysis...")
    count = 0

    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as outfile:
        # Export core project files
        for rel_path in SPECIFIC_FILES:
            full_path = os.path.join(BASE_DIR, rel_path)
            if os.path.exists(full_path):
                outfile.write(f"\n\n{'=' * 80}\n")
                outfile.write(f"FILE: {rel_path}\n")
                outfile.write(f"{'=' * 80}\n\n")
                with open(full_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                count += 1

        # Scan apps for structural backend files
        for root, dirs, files in os.walk(BASE_DIR):
            if any(x in root for x in ['venv', '.git', '__pycache__', 'migrations']):
                continue

            for file in files:
                if file in TARGET_FILES:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, BASE_DIR)

                    outfile.write(f"\n\n{'=' * 80}\n")
                    outfile.write(f"FILE: {rel_path}\n")
                    outfile.write(f"{'=' * 80}\n\n")

                    with open(full_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                    count += 1

    print(f"Done! Compiled {count} files into '{OUTPUT_FILENAME}'.")


if __name__ == '__main__':
    export_backend()