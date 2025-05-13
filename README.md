# Receipt Information Extractor (uctenka.py)

This Python script uses the Google Gemini API to extract structured information (company name, VAT number, prices, etc.) from PDF or image files representing receipts or when modified even invoices. It processes files prefixed with "uctenka_" and outputs the extracted data as a JSON file for each input.

## Features

*   Extracts key details from receipt documents using power of Gemini 2.0 Flash.
*   Supports PDF files and common image formats (e.g., JPG, PNG).
*   Utilizes the Google Gemini API.
*   Outputs extracted data in a structured JSON format.
*   Automatically processes all files in its directory starting with `uctenka_`.
*   Saves a corresponding `.json` file for each processed input file.

## Prerequisites

*   Python 3.7+
*   A Google Gemini API Key. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).
*   The `google-generativeai` Python package.

## Setup

1.  **Clone or Download:**
    Get the `uctenka.py` script and place it in your desired project directory.

2.  **Create a Virtual Environment (Recommended):**
    Navigate to your project directory in the terminal and create a virtual environment:
    ```bash
    python3 -m venv .venv
    ```
    Activate the virtual environment:
    *   **macOS / Linux:**
        ```bash
        source .venv/bin/activate
        ```
    *   **Windows (Command Prompt):**
        ```bash
        .\.venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell):**
        ```bash
        .\.venv\Scripts\Activate.ps1
        ```

3.  **Install Dependencies:**
    With the virtual environment active, install the required package:
    ```bash
    pip install google-generativeai
    ```

## Configuration

1.  **Set API Key:**
    Open the `uctenka.py` script in a text editor.
    Find the line:
    ```python
    GEMINI_API_KEY = "YOUR_API_KEY_HERE"
    ```
    Replace `"YOUR_API_KEY_HERE"` with your actual Google Gemini API key.

## Usage

1.  **Place Input Files:**
    Copy your receipt/invoice files (PDFs or images like JPG, PNG) into the same directory as the `uctenka.py` script.
    **Important:** Your input files must be named with the prefix `uctenka_` (e.g., `uctenka_001.pdf`, `uctenka_shop_receipt.jpg`).

2.  **Run the Script:**
    Ensure your virtual environment is activated. Then, from the terminal (while in the project directory), run the script:
    ```bash
    python3 uctenka.py
    ```

3.  **Output:**
    *   The script will print the progress and the extracted JSON data for each file to the terminal.
    *   For each processed input file (e.g., `uctenka_001.pdf`), a corresponding JSON file (e.g., `uctenka_001.json`) containing the extracted data will be saved in the same directory.

## Troubleshooting

*   **`ImportError` or `ModuleNotFoundError`:** Ensure your virtual environment is active and you have run `pip install google-generativeai` within it.
*   **API Key Errors (e.g., authentication issues):**
    *   Double-check that you have correctly replaced `"YOUR_API_KEY_HERE"` in the script with your valid API key.
    *   Ensure your API key has the necessary permissions and your Google Cloud project (if applicable) is set up correctly.
*   **"No files found with prefix 'uctenka_'"**: Make sure your input files are in the same directory as the script and their names start with `uctenka_`.
*   **"Unsupported file type"**: The script primarily supports common image formats and PDFs. Check the `get_mime_type` function if you encounter issues with specific file types.
