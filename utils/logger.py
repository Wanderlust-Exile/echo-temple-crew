import os

def save_output_to_file(filename: str, content: str):
    """Writes the given content to a file inside the outputs/ directory."""
    # Build the full output path
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    
    # Write content to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
