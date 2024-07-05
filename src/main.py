import os
import subprocess
import platform
import webbrowser
from colorama import init, Fore, Style
from anthropic import Anthropic
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
from pygments import highlight
from tavily import TavilyClient
import pygments.util
import base64
import io
from PIL import Image
from system_prompt import get_system_prompt
from dotenv import load_dotenv

#Initializing
init()
load_dotenv()

#Colors
USER_COLOR = Fore.WHITE
CLAUDE_COLOR = Fore.LIGHTMAGENTA_EX
TOOL_COLOR = Fore.BLUE
RESULT_COLOR = Fore.GREEN

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))


conversation_history = []


def print_colored(text, color):
    print(f"{color}{text}{Style.RESET_ALL}")
    
def print_code(code, language):
    try:
        lexer = get_lexer_by_name(language, stripall=True)
        formatted_code = highlight(code, lexer, TerminalFormatter())
        print(formatted_code)
    except pygments.util.ClassNotFound:
        print_colored(f"Code (language: {language}):\n{code}", CLAUDE_COLOR)
        
        
# --------------- APPLICATION MANIPULATION --------------- #

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {path}"
    except Exception as e:
        return f"Error creating folder: {str(e)}"
    

def create_file(path, content=""):
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"File created: {path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"
    

def write_to_file(path, content):
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"Content written to file: {path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

    
def read_file(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {path}"
    
    
def list_files(path="."):
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"
    

# --------------- ADDED FUNCTIONALITY --------------- #

def tavily_search(query):
    try:
        response = tavily.qna_search(query=query, search_depth="advanced")
        return response
    except Exception as e:
        return f"Error performing search: {str(e)}"
    
    
def execute_script(path):
    try:
        script_dir = os.path.dirname(os.path.abspath(path))
        original_dir = os.getcwd()
        os.chdir(script_dir)
        
        file_extension = os.path.splitext(path)[1].lower()
        
        
        if platform.system() == "Windows":
            if file_extension == ".py":
                command = ["py", os.path.basename(path)]
            elif file_extension == ".js":
                command = ["node", os.path.basename(path)]
            elif file_extension in ['.sh', '.bash']:
                command = ["bash", os.path.basename(path)]
            elif file_extension == '.ps1':
                command = ["powershell", "-File", os.path.basename(path)]
            elif file_extension == '.html':
                webbrowser.open(os.path.abspath(path))
                os.chdir(original_dir)
                return f"HTML file opened in default web browser."
            else:
                return f"Unsupported file type: {file_extension}"
        
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=None)
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            return f"Script executed successfully: Output:\n{result.stdout}"
        else:
            return f"Script execution failed - Error:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Script execution timed out after 45 seconds."
    except Exception as e:
        return f"Error executing the script: {str(e)}"
    finally:
        os.chdir(original_dir)


def find_script(script_path):
    if os.path.isfile(script_path):
        return script_path
    else:
        for ext in ['.py', '.js', '.sh', '.bash', '.ps1', '.html']:
            if os.path.isfile(script_path + ext):
                return script_path + ext
    return None
    
      
# ---------------- TOOLS ---------------- #

tools = [
    {
        "name": "create_folder",
        "description": "Create a new folder at the specified path. Use this when you need to create a new directory in the project structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path where the folder should be created"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "create_file",
        "description": "Create a new file at the specified path with optional content. Use this when you need to create a new file in the project structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path where the file should be created"
                },
                "content": {
                    "type": "string",
                    "description": "The initial content of the file (optional)"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_to_file",
        "description": "Write content to an existing file at the specified path. Use this when you need to add or update content in an existing file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "the path of the file to write to"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the file to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_files",
        "description": "List all files and directories in the root folder where the script is running. Use this when you need to see the contents of the current directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the foder to list (default: current directory)"
                }
            }
        }
    },
    {
        "name": "tavily_search",
        "description": "Perform a web search using Tavily API to get up-to-date information or additional context. Use this when you need current information or feel a search could provide a better answer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "execute_script",
        "description": "Execute a script at the specified path. Supports Python, JavaScript, Bash, and PowerShell scripts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the Python script to execute"
                }
            },
            "required": ["path"]
        }
    }
]
    

# ------------------ MAIN ------------------ #

def execute_tool(tool_name, tool_input):
    if tool_name == "create_folder":
        return create_folder(tool_input["path"])
    elif tool_name == "create_file":
        return create_file(tool_input["path"], tool_input.get("content", ""))
    elif tool_name == "write_to_file":
        return write_to_file(tool_input["path"], tool_input.get("content", ""))
    elif tool_name == "read_file":
        return read_file(tool_input["path"])
    elif tool_name == "list_files":
        return list_files(tool_input.get("path", "."))
    elif tool_name == "tavily_search":
        return tavily_search(tool_input["query"])
    elif tool_name == "execute_script":
        return execute_script(tool_input["path"])
    else:
        return f"Unknown tool: {tool_name}"
    
    
def encode_image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    except Exception as e:
        return f"Error encoding image: {str(e)}"
    
    
def chat_with_claude(user_input, image_path=None):
    global conversation_history
    
    if image_path:
        print_colored(f"Processing image at path: {image_path}", TOOL_COLOR)
        image_base64 = encode_image_to_base64(image_path)
        
        if image_base64.startswith("Error"):
            print_colored(f"Error encoding image: {image_base64}", TOOL_COLOR)
            return "Sorry, there was an error processing the image, please try again!"
        
        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64
                    }
                },
                {
                    "type": "text",
                    "text": f"User input for image: {user_input}"
                }
            ]
        }
        conversation_history.append(image_message)
        print_colored("Image message added to conversation history", TOOL_COLOR)
    else:
        conversation_history.append({"role": "user", "content": user_input})
         
    messages = [msg for msg in conversation_history if msg.get('content')]
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system=get_system_prompt(),
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"}
        )
    except Exception as e:
        print_colored(f"Error calling Claude API: {str(e)}", TOOL_COLOR)
        return "Sorry, there is an error communication with the Claude API at this time, please try again!"
    
    assistant_response = ""
    
    for content_block in response.content:
        if content_block.type == "text":
            assistant_response += content_block.text
            print_colored(f"\nClaude: {content_block.text}", CLAUDE_COLOR)
        elif content_block.type == "tool_use":
            tool_name = content_block.name
            tool_input = content_block.input
            tool_use_id = content_block.id
            
            print_colored(f"\nTool Used: {tool_name}", TOOL_COLOR)
            print_colored(f"Tool Input: {tool_input}", TOOL_COLOR)
            
            result = execute_tool(tool_name, tool_input)
            print_colored(f"Tool Result: {result}", RESULT_COLOR)
            
            conversation_history.append({"role": "assistant", "content": [content_block]})
            conversation_history.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    }
                ]
            })
            
            try:
                tool_response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4000,
                    system=get_system_prompt(),
                    messages=[msg for msg in conversation_history if msg.get('content')],
                    tools=tools,
                    tool_choice={"type": "auto"}    
                )
            
                for tool_content_block in tool_response.content:
                    if tool_content_block.type == "text": 
                        assistant_response += tool_content_block.text
                        print_colored(f"\nClaude: {tool_content_block.text}", CLAUDE_COLOR)
            except Exception as e:
                print_colored(f"Error in tool response: {str(e)}", TOOL_COLOR)
                assistant_response += "\nI encountered an error while processing the tool result, please try again!"
                
                
    if assistant_response:
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
    return assistant_response


def process_and_display_result(response):
    if response.startswith("Error") or response.startswith("I'm sorry"):
        print_colored(response, TOOL_COLOR)
    else:
        if "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    print_colored(part, CLAUDE_COLOR)
                else:
                    lines = part.split('\n')
                    language = lines[0].strip() if lines else ""
                    code = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                    
                    if language and code:
                        print_code(code, language)
                    elif code:
                        print_colored(f"Code:\n{code}", CLAUDE_COLOR)
                    else:
                        print_colored(part, CLAUDE_COLOR)   
        else:
            print_colored(response, CLAUDE_COLOR)
            
            
def main():
    global conversation_history
    print_colored("Welcome to Your Local Claude Chat With Image Support!", CLAUDE_COLOR)
    print_colored("Type 'exit' to end the conversation.", CLAUDE_COLOR)
    print_colored("Type 'image' to include an image in your message.", CLAUDE_COLOR)
    print_colored("You can also ask to run python scripts! - (Type 'Run {script_name}')", CLAUDE_COLOR)
    print_colored("Supported script types: Python (.py), JavaScript (.js), Bash (.sh, .bash), PowerShell (.ps1), HTML (.html)", CLAUDE_COLOR)
    
    while True:
        user_input = input(f"\n\n{USER_COLOR}You: {Style.RESET_ALL}")
        
        if user_input.lower() == 'exit':
            print_colored("Thanks for chatting, see you soon!", CLAUDE_COLOR)
            break
        
        if user_input.lower() == 'image':
            image_path = input(f"{USER_COLOR}Drag and drop your image here: {Style.RESET_ALL}")
            
            # Remove quotes and normalize path
            image_path = image_path.strip().strip("\"'")
            image_path = os.path.normpath(image_path)
            
            if os.path.isfile(image_path):
                user_input = input(f"{USER_COLOR}You (prompt for image): {Style.RESET_ALL}")
                response = chat_with_claude(user_input, image_path)
                process_and_display_result(response)
            else:
                print_colored(f"Invalid image path: {image_path}\nPlease try again!", CLAUDE_COLOR)
                continue
        elif user_input.lower().startswith("run "):
            script_path = user_input[4:].strip()
            full_path = os.path.abspath(script_path)
            script = find_script(script_path)
            
            if script is None:
                print_colored(f"No script matching 'script_name' found at '{full_path}'.", CLAUDE_COLOR)
            else:
                print_colored(f"Attempting to run: {script}", CLAUDE_COLOR)
                result = execute_script(script)
                print_colored(result, RESULT_COLOR)
        else:
            response = chat_with_claude(user_input)
            process_and_display_result(response)
            
            
            
if __name__ == "__main__":
    main()
            
            
