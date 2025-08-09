from crewai.tools import tool

def _test() -> str:
    """A simple test tool that returns success."""
    return "Success"

test = tool("test_tool")(_test)

print(test.run())  # ✅


