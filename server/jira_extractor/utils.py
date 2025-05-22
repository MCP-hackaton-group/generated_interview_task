import json
import re
import ast

def extract_json_from_response(response_text):
    """
    Extracts and parses JSON data from a response text.
    First tries to find JSON pattern, then applies multiple parsing approaches.

    Args:
        response_text (str): A string containing JSON data somewhere within it

    Returns:
        dict: The parsed JSON data as a Python dictionary
    """
    try:
        # Step 1: Use regex to find JSON pattern in response (original approach)
        json_match = re.search(r'{.*}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON found in the response.")

        json_str = json_match.group()

        # Step 2: Try direct parsing
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Step 3: Handle single quotes vs double quotes issue
        normalized = json_str.replace("\\'", "___ESCAPED_SINGLE_QUOTE___")
        normalized = re.sub(r"(?<![\\])\'", "\"", normalized)
        normalized = normalized.replace("___ESCAPED_SINGLE_QUOTE___", "\\'")

        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            pass

        # Step 4: More aggressive cleaning for malformed JSON
        cleaned = json_str.strip()
        cleaned = re.sub(r"(?<![\\])\'", "\"", cleaned)
        cleaned = re.sub(r'(?<!")(\w+)(?=":)', r'"\1"', cleaned)
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*]', ']', cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Step 5: Last resort - use ast.literal_eval
        try:
            return ast.literal_eval(json_str)
        except:
            raise ValueError(f"Failed to parse JSON after multiple attempts: {json_str[:50]}...")

    except Exception as e:
        raise ValueError(f"Error processing JSON: {str(e)}")