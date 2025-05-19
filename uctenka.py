import os
import glob
import mimetypes
import json

import google.generativeai as genai

# --- Configuration ---
GEMINI_API_KEY = "YOUR_API_KEY_HERE" 
MODEL_NAME = "gemini-2.0-flash-001"

# --- Helper to get MIME type ---
def get_mime_type(file_path):
    """Guesses the MIME type of a file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        if file_path.lower().endswith(".pdf"): return "application/pdf"
        if file_path.lower().endswith((".jpg", ".jpeg")): return "image/jpeg"
        if file_path.lower().endswith(".png"): return "image/png"
    return mime_type

def extract_info_from_file(file_path):
    """
    Extracts receipt information from a given image or PDF file using Gemini API.
    """
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE" or not GEMINI_API_KEY:
        print("ERROR: Please replace 'YOUR_API_KEY_HERE' with your actual Gemini API key in the script.")
        return None

    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring Gemini library: {e}")
        print("Please ensure your API key is correct.")
        return None

    mime_type = get_mime_type(file_path)
    if not mime_type:
        print(f"Could not determine MIME type for {file_path}. Skipping.")
        return None

    supported_mime_prefixes = ["image/", "application/pdf"]
    if not any(mime_type.startswith(prefix) for prefix in supported_mime_prefixes):
        print(f"Unsupported file type: {mime_type} for {file_path}. Skipping. Supported: images, PDF.")
        return None

    print(f"\n--- Processing file: {file_path} (MIME type: {mime_type}) ---")

    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

    prompt_text = """
    Extract the following details from the provided receipt document (image or PDF). First look for VAT identification number (vatNumber) in the document and associated name of the company (companyName).
    Ensure all fields from the schema are populated if the information is present in the document.
    If a piece of information is not found, you may omit the field or use a suitable placeholder like 'N/A' if the schema requires it,
    but prioritize extracting actual values. For numerical values (prices, VAT amount, VAT rate), provide them as numbers (float).
    For VAT rate, if it's written as e.g. '21%', provide the number 21.
    Also, extract the date of sale (transaction date) from the receipt. It might be in dd/mm/yyyy or dd.mm.yyyy format. If multiple dates are present (e.g., issue date, due date), use the primary transaction/sale date.
    """

    contents = [
        prompt_text,
        {"mime_type": mime_type, "data": file_data}
    ]

    try:
        # Attempt to use genai.Type directly for schema definition
        schema_type_object = genai.Type.OBJECT
        schema_type_string = genai.Type.STRING
        schema_type_number = genai.Type.NUMBER
    except AttributeError:
        # Fallback if genai.Type is not directly accessible
        print("Warning: genai.Type not directly accessible, using string representations for schema types.")
        schema_type_object = "OBJECT"
        schema_type_string = "STRING"
        schema_type_number = "NUMBER"

    response_schema_dict = {
        "type": schema_type_object,
        "required": ["companyName", "vatNumber", "priceWithoutVAT", "vat", "vatRate", "priceIncludingVAT", "dateOfSale"], 
        "properties": {
            "companyName": {"type": schema_type_string, "description": "The legal name of the company that issued the receipt always associated with the VAT identification number. Legal name always includes legal form (e.g. s.r.o., a.s. etc.)"},
            "vatNumber": {"type": schema_type_string, "description": "The VAT identification number of the company."},
            "priceWithoutVAT": {"type": schema_type_number, "format": "float", "description": "The total price of goods/services before VAT is applied. Use 0.0 if not explicitly found."},
            "vat": {"type": schema_type_number, "format": "float", "description": "The total VAT amount charged. Use 0.0 if not explicitly found."},
            "vatRate": {"type": schema_type_number, "format": "float", "description": "The VAT rate as a percentage (e.g., 21 for 21%). Use 0.0 if not explicitly found."},
            "priceIncludingVAT": {"type": schema_type_number, "format": "float", "description": "The final price including VAT. This is usually the most prominent total amount."},
            "dateOfSale": {"type": schema_type_string, "description": "The date of sale or transaction date from the receipt, in dd.mm.yyyy format."} 
        }
    }

    generation_config_dict = {
        "temperature": 0.2,
        "response_mime_type": "application/json",
        "response_schema": response_schema_dict
    }

    response = None
    try:
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content(
            contents=contents,
            generation_config=generation_config_dict,
        )

        if response.text:
             return response.text
        elif response.parts:
             print("Warning: Accessing response via parts[0].text as response.text was empty.")
             return response.parts[0].text
        else:
             feedback_info = "N/A"
             if response and hasattr(response, 'prompt_feedback'):
                 feedback_info = str(response.prompt_feedback)
             print(f"Error: Gemini API returned an empty response (no text or parts). Feedback: {feedback_info}")
             return None

    except Exception as e:
        exception_type_name = type(e).__name__
        print(f"An error occurred while calling Gemini API for {file_path}: {e}")
        feedback_info = "N/A"
        finish_reason = "N/A"
        if response and hasattr(response, 'prompt_feedback'):
            feedback_info = str(response.prompt_feedback)
        finish_reason = getattr(e, 'finish_reason', 'N/A')
        print(f"Exception Type: {exception_type_name}")
        print(f"Prompt Feedback (if available): {feedback_info}")
        print(f"Finish Reason (if available): {finish_reason}")
        return None


if __name__ == "__main__":
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE" or not GEMINI_API_KEY:
        print("CRITICAL: Please set your GEMINI_API_KEY in the script before running.")
    else:
        files_to_process = glob.glob("uctenka_*.*")
        if not files_to_process:
            print("No files found with prefix 'uctenka_' in the current directory.")
            print("Please add some files like 'uctenka_001.pdf' or 'uctenka_shop.jpg'.")
        else:
            print(f"Found {len(files_to_process)} files to process: {files_to_process}")
            for file_path in files_to_process:
                json_output = extract_info_from_file(file_path)
                if json_output:
                    print(f"Extracted JSON for {os.path.basename(file_path)}:")
                    print(json_output)

                    base_name = os.path.basename(file_path)
                    file_name_without_ext = os.path.splitext(base_name)[0]
                    output_json_filename = file_name_without_ext + ".json"

                    try:
                        parsed_json = json.loads(json_output)
                        with open(output_json_filename, "w", encoding="utf-8") as f_out:
                            json.dump(parsed_json, f_out, indent=2, ensure_ascii=False)
                        print(f"Saved JSON to {output_json_filename}")
                    except json.JSONDecodeError:
                         print(f"Error: Output from API for {base_name} was not valid JSON. Saving raw output.")
                         output_raw_filename = file_name_without_ext + ".txt"
                         try:
                             with open(output_raw_filename, "w", encoding="utf-8") as f_out:
                                 f_out.write(json_output)
                             print(f"Saved raw output to {output_raw_filename}")
                         except Exception as e_raw:
                             print(f"Error saving raw output to file {output_raw_filename}: {e_raw}")
                    except Exception as e:
                        print(f"Error saving JSON to file {output_json_filename}: {e}")

            print("\n--- Processing complete. ---")
