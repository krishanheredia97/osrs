import os
import shutil
import subprocess


def convert_files_to_txt(project_dirs, file_names, output_dir):
    """
    Converts specified files in multiple project directories to .txt files in an output directory.

    Args:
        project_dirs (list): A list of paths to the project directories.
        file_names (list): A list of file names (without extensions) to convert.
        output_dir (str): The path to the output directory where the .txt files will be saved.

    Returns:
        None
    """
    # Delete all files in the output directory
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    for project_dir in project_dirs:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_name, file_ext = os.path.splitext(file)
                if file_name in file_names:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(output_dir, f"{file_name}{file_ext}.txt")
                    with open(src_file, 'r') as f:
                        content = f.read()
                    with open(dest_file, 'w') as f:
                        f.write(content)
                    print(f"Created {dest_file}")
                    with open(os.path.join(output_dir, "0_LAST_INPUT.txt"), "w") as f:
                        f.write(file_names_input)


def open_output_directory(output_dir):
    """
    Opens the output directory using the default file explorer.

    Args:
        output_dir (str): The path to the output directory to open.

    Returns:
        None
    """
    try:
        if os.name == 'nt':  # For Windows
            os.startfile(output_dir)
        elif os.name == 'posix':  # For macOS and Linux
            subprocess.call(['open', output_dir])
        else:
            print(f"Unable to open the directory automatically. Please navigate to: {output_dir}")
    except Exception as e:
        print(f"Error opening the directory: {e}")


if __name__ == "__main__":
    output_dir = r"C:\Users\danie\OneDrive\Escritorio\Coding\PYTHON\osrs"
    file_names_input = input("Enter the file names (separated by commas) to convert: ")
    file_names = [name.strip().replace(" ", "_") for name in file_names_input.split(", ")]

    project_dirs = [
        r"C:\Users\danie\PycharmProjects\osrs"
    ]

    convert_files_to_txt(project_dirs, file_names, output_dir)

    print(f"\nFiles have been converted and saved to: {output_dir}")
    open_output_directory(output_dir)