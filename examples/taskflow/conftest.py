import os
import tempfile

# Use a throwaway SQLite file for tests. Must be set before app.main is imported.
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
