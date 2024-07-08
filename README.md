# AI-Powered Engineering Assistant

## Overview
This project implements an AI-powered assistant designed to autonomously interact with users, manage files, execute scripts, and perform web searches to provide comprehensive support in various engineering tasks. The system leverages advanced language models to iteratively refine its responses and improve its functionality.

## Key Components
1. **Agent**: The main orchestrator that manages the overall process and interaction.
2. **FileManager**: Handles file creation, reading, writing, and directory management.
3. **ScriptExecutor**: Executes scripts in various languages (Python, JavaScript, Bash, PowerShell, HTML).
4. **WebSearcher**: Uses the Tavily API for performing web searches and retrieving information.
5. **ImageProcessor**: Processes and converts images for inclusion in conversations.

## Features
* Conversational interface for user interaction
* Iterative response refinement using AI models
* File and directory management
* Script execution for multiple programming languages
* Web content retrieval with error handling
* Image processing and encoding
* Integration with Anthropic and Tavily APIs

## Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/bosmanbos/AI-Powered-Engineering-Assistant.git
    ```
2. Navigate to the project directory:
    ```bash
    cd AI-Powered-Engineering-Assistant
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Create a `.env` file in the project directory with your API keys:
    ```
    ANTHROPIC_API_KEY=your_anthropic_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```

## Usage
1. Run the main script:
    ```bash
    python ./src/main.py
    ```
2. Follow the prompts in the terminal to interact with the assistant.
    * Type your queries or commands.
    * Use `image` to include an image in your message.
    * Use `run {script_name}` to execute a script.
    * Type `exit` to end the conversation.

## Configuration
Adjust the following parameters in `main.py` or other configuration files as needed:
* `model`: The main language model to use (e.g., 'claude-3-5-sonnet-20240620')
* `tools`: Configuration for the integrated tools and their behaviors

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License.
