import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from crew import crew

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n=== Final Output ===\n")
    print(result)

from dotenv import load_dotenv
load_dotenv()

