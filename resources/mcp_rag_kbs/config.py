from pathlib import Path

# Path settings
DB_DIR = Path(__file__).parent / "db"
DB_INDEX_NAME = "kbs_faiss_db"

# PARSING_OUTPUT_KBS_DIR = Path(__file__).parent / "parsing_outputs/kbs/4a414ed1-67ae-49f6-acf5-a92ad7a3c206"
PARSING_OUTPUT_KBS_DIR = Path(__file__).parent / "parsing_outputs/kbs/8bd71afa-3ed8-450e-a8ef-9f609a403daf"

# Default settings
# DEFAULT_CHUNK_SIZE = 1000
# DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 4
DEFAULT_EMBEDDING_MODEL = "upstage"
DEFAULT_LLM_MODEL = "gpt-4.1-mini"