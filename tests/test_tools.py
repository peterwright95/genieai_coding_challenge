import os
import tempfile
import pytest
import time
from types import SimpleNamespace
from chat_interface.cli_chat import BASE_DIR
from tools.file_tools import (
    _safe_path,
    list_files,
    read_file,
    write_file,
    delete_file,
    answer_question_about_files,
)

from agent.base_agent import build_agent
from agent.question_filtering_agent import build_filter_agent

@pytest.fixture
def temp_workspace():
    """Creates a temporary workspace directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def ctx(temp_workspace):
    """Provides a mocked RunContext with base_directory."""
    return SimpleNamespace(deps={"base_directory": temp_workspace})

def test_write_and_read_file(ctx):
    res = write_file(ctx, "test.txt", "Hello World")
    assert "successfully" in res
    content = read_file(ctx, "test.txt")
    assert content == "Hello World"

def test_append_file(ctx):
    write_file(ctx, "test.txt", "Start")
    write_file(ctx, "test.txt", " End", mode="a")
    content = read_file(ctx, "test.txt")
    assert content == "Start \n End"

def test_list_files(ctx):
    write_file(ctx, "file1.txt", "Data")
    write_file(ctx, "file2.txt", "More")
    files = list_files(ctx)
    assert len(files) == 2
    filenames = [f["filename"] for f in files]
    assert "file1.txt" in filenames
    assert "file2.txt" in filenames

def test_delete_file(ctx):
    write_file(ctx, "todelete.txt", "Bye")
    assert os.path.exists(_safe_path(ctx, "todelete.txt"))
    res = delete_file(ctx, "todelete.txt")
    assert "successfully" in res
    assert not os.path.exists(_safe_path(ctx, "todelete.txt"))

def test_read_nonexistent_file(ctx):
    res = read_file(ctx, "missing.txt")
    assert "does not exist" in res

def test_invalid_write_mode(ctx):
    res = write_file(ctx, "fail.txt", "data", mode="x")
    assert "Invalid mode" in res

def test_answer_question_about_files(ctx):
    write_file(ctx, "first.txt", "Alpha")
    write_file(ctx, "second.txt", "Beta")
    response = answer_question_about_files(ctx, "Where is Alpha?")
    assert "FILE SUMMARY" in response
    assert "Alpha" in response
    assert "Beta" in response

def test_safe_path_invalid_filename(ctx):
    with pytest.raises(ValueError):
        _safe_path(ctx, "")

def test_read_unreadable_file(ctx):
    file_path = os.path.join(ctx.deps["base_directory"], "secret.txt")
    with open(file_path, "w") as f:
        f.write("top secret")
    os.chmod(file_path, 0o000)  # Remove all permissions
    try:
        res = read_file(ctx, "secret.txt")
        assert "permission" in res.lower()
    finally:
        os.chmod(file_path, 0o644)  # Restore permissions for cleanup

def test_read_directory_instead_of_file(ctx):
    os.mkdir(os.path.join(ctx.deps["base_directory"], "subdir"))
    res = read_file(ctx, "subdir")
    assert "is a directory" in res or "directory" in res.lower()

def test_write_to_readonly_file(ctx):
    file_path = os.path.join(ctx.deps["base_directory"], "readonly.txt")
    with open(file_path, "w") as f:
        f.write("can't touch this")
    os.chmod(file_path, 0o444)  # Read-only
    try:
        res = write_file(ctx, "readonly.txt", "try to write")
        assert "permission" in res.lower()
    finally:
        os.chmod(file_path, 0o644)  # Restore permissions for cleanup

def test_delete_directory_instead_of_file(ctx):
    dir_path = os.path.join(ctx.deps["base_directory"], "adir")
    os.mkdir(dir_path)
    res = delete_file(ctx, "adir")
    assert "directory" in res.lower()

@pytest.mark.asyncio
async def test_agent_chained_tool_use(temp_workspace):
    """Test agent reasoning through multiple tool calls."""
    
    # Prepopulate files
    with open(os.path.join(temp_workspace, "a.txt"), "w") as f:
        f.write("Old File")
    time.sleep(1)
    with open(os.path.join(temp_workspace, "b.txt"), "w") as f:
        f.write("New File")

    # Run agent with prompt that requires planning
    base_agent = build_agent(str(temp_workspace))
    result = await base_agent.run("Read me the latest modified file", deps={"base_directory": temp_workspace})

    assert "New File" in result.output
    
@pytest.mark.asyncio
async def test_agent_list_files(temp_workspace):
    """Test agent listing files."""
    
    with open(os.path.join(temp_workspace, "file1.txt"), "w") as f:
        f.write("Data1")
    with open(os.path.join(temp_workspace, "file2.txt"), "w") as f:
        f.write("Data2")

    base_agent = build_agent(str(temp_workspace))
    result = await base_agent.run("List all files", deps={"base_directory": temp_workspace})

    assert "file1.txt" in result.output
    assert "file2.txt" in result.output
    
@pytest.mark.asyncio
async def test_agent_read_specific_file(temp_workspace):
    """Test agent reading a specific file by name."""
    
    with open(os.path.join(temp_workspace, "readme.txt"), "w") as f:
        f.write("Important Content")

    base_agent = build_agent(str(temp_workspace))
    result = await base_agent.run("Please read the file called readme.txt", deps={"base_directory": temp_workspace})

    assert "Important Content" in result.output
    
@pytest.mark.asyncio
async def test_agent_write_new_file(temp_workspace):
    """Test that the agent creates the file with correct content."""
    
    base_agent = build_agent(str(temp_workspace))
    result = await base_agent.run(
        "Create a file named notes.txt with the content Hello World",
        deps={"base_directory": temp_workspace}
    )

    file_path = os.path.join(temp_workspace, "notes.txt")

    # Confirm file exists
    assert os.path.isfile(file_path), "File was not created."

    # Confirm file content
    with open(file_path, "r") as f:
        content = f.read()

    assert "hello world" in content.lower()
    
@pytest.mark.asyncio
async def test_agent_delete_file(temp_workspace):
    """Test agent deleting a file with actual filesystem check."""
    
    filepath = os.path.join(temp_workspace, "todelete.txt")
    with open(filepath, "w") as f:
        f.write("Temporary content")

    assert os.path.exists(filepath)  # Sanity check

    base_agent = build_agent(str(temp_workspace))
    result = await base_agent.run("Delete the file todelete.txt", deps={"base_directory": temp_workspace})

    assert not os.path.exists(filepath), "File should be deleted"

@pytest.mark.asyncio
async def test_filter_agent_declines_irrelevant_request():
    """Test filter agent rejecting unrelated prompts."""
    
    filter_agent = build_filter_agent()
    result = await filter_agent.run("What is the meaning of life?")
    
    assert result.output.strip().lower() == "reject"
    
@pytest.mark.asyncio
async def test_filter_agent_allows_file_request():
    """Test filter agent accepting valid file-related prompts."""
    
    filter_agent = build_filter_agent()
    result = await filter_agent.run("Please list all files in the workspace")
    
    assert result.output.strip().lower() == "accept"
    
@pytest.mark.asyncio
async def test_agent_rejects_path_traversal(temp_workspace):
    """Ensure agent refuses unsafe filenames with directory traversal."""
    
    base_agent = build_agent(str(temp_workspace))
    result = await base_agent.run(
        "Create a file named ../outside.txt with the content Should fail",
        deps={"base_directory": temp_workspace}
    )

    # Confirm no such file created inside workspace
    assert "outside.txt" not in os.listdir(temp_workspace)
    
@pytest.mark.asyncio
async def test_agent_rejects_delete_directory(temp_workspace):
    """Agent should refuse to delete directories using file delete tool."""
    
    dir_path = os.path.join(temp_workspace, "somedir")
    os.mkdir(dir_path)

    base_agent = build_agent(str(temp_workspace))
    result = await base_agent.run(
        "Delete the directory somedir",
        deps={"base_directory": temp_workspace}
    )

    assert os.path.exists(dir_path)
    
