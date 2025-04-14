import os


# Set your OpenAI API key here
 # <-- Replace this with your real key

def list_files(folder_path):
    try:
        files = os.listdir(folder_path)
        files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            print("No files found in the folder.")
            return []
        print("\nFiles in folder:")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        return files
    except FileNotFoundError:
        print("Folder not found.")
        return []

def validate_sequence(files, seq_num):
    if seq_num.isdigit():
        seq_index = int(seq_num) - 1
        if 0 <= seq_index < len(files):
            return files[seq_index]
        else:
            print("Invalid file sequence number.")
    else:
        print("Sequence number should be a digit.")
    return None

def handle_prompts():
    prompts = {
        "1": "PRD review",
        "2": "Create Tech Spec from PRD",
        "3": "Tech Spec Review"
    }

    print("\nChoose a prompt:")
    for key, value in prompts.items():
        print(f"{key}. {value}")

    user_input = input("Enter prompt number: ").strip()

    if user_input in prompts:
        return prompts[user_input]
    else:
        print("Prompt is wrong.")
        return None


def main():
    folder_path = input("Enter the folder path: ").strip()
    files = list_files(folder_path)

    if not files:
        return

    seq_num = input("\nEnter the file sequence number: ").strip()
    selected_file = validate_sequence(files, seq_num)

    if selected_file:
        file_path = os.path.join(folder_path, selected_file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            print(f"Could not read file: {e}")
            return

        selected_prompt = handle_prompts()
        if selected_prompt:
            print(f"\nSelected Prompt: {selected_prompt}")
            print(f"\nFile: {selected_file}")
            print(f"\nFile Content:\n{'-'*40}\n{file_content}")
    else:
        print("File is not correct.")

if __name__ == "__main__":
    main()
