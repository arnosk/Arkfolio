# Database setup for sqlite3
DB_TYPE = "sqlite"
DB_CONFIG = {"dbname": "Arkfolio.db"}

# Logging
MAX_SIZE_LOGFILE_MB = 1
NUM_LOGFILES = 5
LOG_PATH = "log"
LOG_FILE = "arkfolio.log"
LOG_LEVEL = "DEBUG"
MAX_CHAR_LOG_SCRIPT_LENGHT = 150

# Output path (relative or absolute)
# Use / or \\ for folders
OUTPUT_PATH = "output"
IMAGE_PATH = "images"

# requests
REQUESTS_TIMEOUT = 20
REQUESTS_RETRIES = 5

# Sitemodels
BLOCKCHAININFO_BACKOFF = 15
CHILD_ADDRESS_BATCH_SIZE = 10
