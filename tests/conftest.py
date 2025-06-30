import os
import shutil
import pytest

@pytest.fixture
def temp_workspace(tmp_path):
    """Provides a temporary workspace directory for testing."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    yield str(workspace)
    shutil.rmtree(str(workspace), ignore_errors=True)