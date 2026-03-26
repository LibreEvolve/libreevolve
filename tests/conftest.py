from dotenv import load_dotenv


# Load project-local API keys before test modules evaluate skip conditions.
load_dotenv(override=True)
