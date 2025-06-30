import os
import time
from pydantic_ai import RunContext

def _safe_path(ctx: RunContext, filename: str) -> str:
    """Resolve absolute, safe path within allowed base directory."""
    base_dir = ctx.deps.get("base_directory")
    if not base_dir:
        raise ValueError("Base directory not provided.")
    
    if not filename or filename.strip() == "":
        raise ValueError("Filename must be provided and cannot be empty.")
    
    return os.path.abspath(os.path.join(base_dir, filename))

def list_files(ctx: RunContext) -> list:
    """
    List all files in the working directory, returning metadata for each file:
    - filename
    - size (bytes)
    - last modified timestamp (human-readable)
    - last modified timestamp (raw seconds since epoch)
    """
    #print("[DEBUG] list_files tool called")
    base_dir = ctx.deps.get("base_directory")
    if not base_dir:
        raise ValueError("Base directory not provided.")

    try:
        files = []
        for file in os.listdir(base_dir):
            file_path = os.path.join(base_dir, file)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": file,
                    "size_bytes": stat.st_size,
                    "modified_time_human": time.ctime(stat.st_mtime),
                    "modified_time_raw": stat.st_mtime
                })
        #print(f"[DEBUG] list_files returning {len(files)} files")
        #print(f"[DEBUG] {files}")
        return files

    except Exception as e:
        #print(f"[DEBUG] list_files error: {e}")
        return [{"error": str(e)}]

def read_file(ctx: RunContext, filename: str) -> str:
    """Return the content of a file within base directory."""
    #print(f"[DEBUG] read_file called for {filename}")
    path = _safe_path(ctx, filename)
    if not os.path.exists(path):
        #print(f"[DEBUG] read_file: {filename} does not exist")
        return f"File '{filename}' does not exist."
    if os.path.isdir(path):
        return f"'{filename}' is a directory, not a file."
    try:
        with open(path, "r") as f:
            content = f.read()
        #print(f"[DEBUG] read_file read {len(content)} characters from {filename}")
        return content
    except PermissionError:
        return f"Permission denied when reading '{filename}'."
    except Exception as e:
        return f"Error reading '{filename}': {e}"

def write_file(ctx: RunContext, filename: str, content: str, mode: str = "w") -> str:
    """
    Create, append, or overwrite content in a file within the base directory.
    
    mode:
      - 'w' = overwrite (default)
      - 'a' = append (adds newline before content automatically)
    """
    if mode not in {"w", "a"}:
        return "Invalid mode. Use 'w' to overwrite or 'a' to append."

    path = _safe_path(ctx, filename)

    if os.path.isdir(path):
        return f"Cannot write to '{filename}': it is a directory."

    try:
        with open(path, mode) as f:
            if mode == "a":
                f.write(" \n" + content)
            else:
                f.write(content)

        action = "Appended to" if mode == "a" else "Wrote to"
        return f"{action} file '{filename}' successfully."

    except PermissionError:
        return f"Permission denied when writing to '{filename}'."
    except Exception as e:
        return f"Error writing to '{filename}': {e}"

def delete_file(ctx: RunContext, filename: str) -> str:
    """Delete a file within base directory."""
    #print(f"[DEBUG] delete_file called for {filename}")
    path = _safe_path(ctx, filename)
    if not os.path.exists(path):
        #print(f"[DEBUG] delete_file: {filename} does not exist")
        return f"File '{filename}' does not exist."
    if os.path.isdir(path):
        return f"'{filename}' is a directory, not a file."
    try:
        os.remove(path)
        #print(f"[DEBUG] delete_file removed {filename}")
        return f"File '{filename}' deleted successfully."
    except PermissionError:
        return f"Permission denied when deleting '{filename}'."
    except Exception as e:
        return f"Error deleting '{filename}': {e}"

def answer_question_about_files(ctx: RunContext, query: str) -> str:
    """
    Provide a structured summary of all files and their contents to help answer the query.
    The model will see file-by-file content, improving its ability to reference sources accurately.
    """
    #print(f"[DEBUG] answer_question_about_files called with query: {query}")
    base_dir = ctx.deps.get("base_directory")
    if not base_dir:
        raise ValueError("Base directory not provided.")

    try:
        files = os.listdir(base_dir)
        if not files:
            #print("[DEBUG] Workspace contains no files")
            return "Workspace contains no files."

        combined_content = "FILE SUMMARY:\n"

        for file in files:
            file_path = os.path.join(base_dir, file)
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    file_content = f.read().strip()
                    combined_content += f"\n--- FILE: {file} ---\n{file_content if file_content else '[Empty file]'}\n"

        #print("[DEBUG] answer_question_about_files compiled content for LLM")
        return (
            f"{combined_content}\n\n"
            f"Based on the file contents above, please answer the following question:\n"
            f"'{query}'"
        )

    except Exception as e:
        #print(f"[DEBUG] answer_question_about_files error: {e}")
        return f"Error analyzing files: {str(e)}"