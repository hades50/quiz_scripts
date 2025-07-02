import sys
import os
import json
import re
from datetime import datetime
from glob import glob

def convert_markdown_to_json(file_path):
    """
    Parses a specially formatted markdown quiz file and converts it into a JSON structure,
    capturing content within ``` blocks for a 'question_markdown' field.
    """
    try:
        file_name = os.path.basename(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()

        questions = []
        current_question = None
        is_in_markdown_block = False

        for raw_line in raw_lines:
            line = raw_line.strip()

            # --- LOGIC FOR MARKDOWN BLOCK (```) ---
            # Check for the start or end of a markdown block
            if line.startswith('```'):
                if not is_in_markdown_block:
                    # Start of the block
                    is_in_markdown_block = True
                    if current_question:
                        current_question['question_markdown'] = raw_line
                else:
                    # End of the block
                    is_in_markdown_block = False
                    if current_question:
                        current_question['question_markdown'] += raw_line
                continue

            # If we are inside a markdown block, append the raw line and continue
            if is_in_markdown_block:
                if current_question:
                    current_question['question_markdown'] += raw_line
                continue

            # Skip empty lines if not in a markdown block
            if not line:
                continue
            
            # --- EXISTING PARSING LOGIC ---
            # Check for a new question header (####)
            if line.startswith('####'):
                if current_question:
                    questions.append(current_question)
                
                # Initialize the new question object with the new field
                current_question = {
                    "question": line[4:].strip(),
                    "picture_url": "",
                    "correct_answer": -1,
                    "options": [],
                    "question_markdown": "" # Add the new field
                }
                continue

            if not current_question:
                continue

            # Check for an image
            image_match = re.match(r'!\[.*\]\((.*)\)', line)
            if image_match:
                current_question["picture_url"] = image_match.group(1)
                continue

            # Check for an option
            option_match = re.match(r'-\s*\[(x| )\]\s*(.*)', line)
            if option_match:
                is_correct = option_match.group(1).lower() == 'x'
                option_text = option_match.group(2).strip()

                current_question["options"].append({
                    "option_text": option_text,
                    "is_correct": is_correct
                })
                
                if is_correct:
                    current_question["correct_answer"] = len(current_question["options"]) - 1
        
        if current_question:
            questions.append(current_question)

        # Get and add the file's last modification time
        last_modified_timestamp = os.path.getmtime(file_path)
        updated_at = datetime.fromtimestamp(last_modified_timestamp).isoformat()
        
        for q in questions:
            q["updated_at"] = updated_at

        # Final JSON structure
        final_data = {
            "name_of_markdown": file_name,
            "questions": questions
        }
        
        return final_data

    except Exception as e:
        print(f"❌ An error occurred while processing '{file_path}': {e}")
        return None

def main():
    """
    Main function to handle command-line arguments and file processing.
    """
    if len(sys.argv) < 2:
        print("Usage: python your_script_name.py <path/to/root_directory>")
        sys.exit(1)

    root_path = sys.argv[1]

    if not os.path.isdir(root_path):
        print(f"Error: The provided path '{root_path}' is not a valid directory.")
        sys.exit(1)

    # Construct a recursive glob pattern to find all .md files
    glob_pattern = os.path.join(root_path, '**', '*.md')
    
    markdown_files = glob(glob_pattern, recursive=True)

    if not markdown_files:
        print(f"No markdown (.md) files found in '{root_path}' or its subdirectories.")
        sys.exit(0)

    print(f"Found {len(markdown_files)} markdown files. Starting conversion...\n")

    for md_file_path in markdown_files:
        print(f"Processing '{md_file_path}'...")
        json_data = convert_markdown_to_json(md_file_path)

        if json_data:
            output_filename = os.path.splitext(md_file_path)[0] + '.json'
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4)
            
            print(f"✅ Successfully converted to '{output_filename}'\n")

if __name__ == "__main__":
    main()
