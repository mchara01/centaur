import os

tools_path = os.path.join(os.path.dirname(__file__), 'result_parsing')

TOOLS = list()

for tool in os.listdir(tools_path):
    tool_name, ext = os.path.splitext(tool)
    tool_path = os.path.join(tools_path, tool_name)
    TOOLS.append(tool_name)
