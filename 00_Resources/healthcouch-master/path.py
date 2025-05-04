import os

def save_directory_structure(path, indent=0, output_file=None):
    # Check if the provided path is a valid directory
    if not os.path.isdir(path):
        print(f"'{path}' is not a valid directory.")
        return
    
    # Write the directory name with proper indentation
    output_file.write("  " * indent + f"[DIR] {os.path.basename(path)}\n")
    
    # List all files and subdirectories in the current directory
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                # Recursive call for subdirectories
                save_directory_structure(entry.path, indent + 1, output_file)
            else:
                # Write file names
                output_file.write("  " * (indent + 1) + f"[FILE] {entry.name}\n")

# Provide the directory you want to print the structure for
directory_path = '.'  # You can replace '.' with any directory path

# Open a file to save the directory structure
with open('directory_structure.txt', 'w') as output_file:
    save_directory_structure(directory_path, output_file=output_file)

print("Directory structure has been saved to 'directory_structure.txt'.")
