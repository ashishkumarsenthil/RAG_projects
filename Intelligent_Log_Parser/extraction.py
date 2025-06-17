from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

html_path = r"C:\Users\akumarse\Documents\Ashish\RAG_project\data\SDLA-CNF-BASICS_log.html"

def extract_text_from_html(html_content):
    """
    Extracts text from HTML content using BeautifulSoup.
    Args:
        html_content (str): The HTML file path as a string.
    Returns:
        str: The extracted text.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_content)  # Use the file path directly
        page.wait_for_timeout(3000)  # Wait 3 seconds

        rendered_html = page.content()  # Or page.inner_text('body')
        
        soup = BeautifulSoup(rendered_html, "html.parser")
        clean_text = soup.get_text(separator="\n", strip=True)
        
        unwanted_keywords = ["Error in resource file", "Error in file", "ERROR"]

        # Split the text into lines
        lines = clean_text.split("\n")

        # Filter lines that do NOT contain any unwanted keyword
        filtered_lines = [line for line in lines if not any(keyword in line for keyword in unwanted_keywords)]
        #print(filtered_lines)
        # Join the filtered lines back into a string
        final_text = "\n".join(filtered_lines)

        with open("./extracted_data/extracted_log_output.txt", "w", encoding="utf-8") as f:
            f.write(final_text)

        browser.close()
extract_text_from_html(html_path)

def clean_robot_log_for_llm_nested(raw_path, output_path):
    with open(raw_path, 'r',encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    formatted = []
    i = 0
    indent = "  "  # Indent nested keywords

    def is_keyword_header(index):
        return lines[index] == "KEYWORD"

    def is_valid_keyword_name(name):
        # Heuristic: ignore library-only lines like 'SeleniumLibrary .'
        return not name.endswith('.') and not name.endswith('..')

    while i < len(lines):
        line = lines[i]

        # --- Test Info ---
        if line == "TEST":
            formatted.append(f"TEST: {lines[i+1]}")
            i += 2
            continue
        elif line == "Full Name:":
            formatted.append(f"Full Name: {lines[i+1]}")
            i += 2
            continue
        elif line == "Tags:":
            formatted.append(f"Tags: {lines[i+1]}")
            i += 2
            continue
        elif line == "Status:":
            formatted.append(f"Status: {lines[i+1]}")
            i += 2
            continue
        elif line == "Message:":
            formatted.append(f"Message: {lines[i+1]}")
            i += 2
            continue

        # --- Keyword Block ---
        elif is_keyword_header(i):
            # Keyword header line found
            keyword_name = lines[i+1] if i + 1 < len(lines) else ""
            sub_keyword = lines[i+2] if i + 2 < len(lines) and not lines[i+2].startswith("Start") else None

            if is_valid_keyword_name(keyword_name):
                formatted.append(f"\nKEYWORD: {keyword_name}")
                if sub_keyword and is_valid_keyword_name(sub_keyword):
                    formatted.append(f"{indent}Sub-keyword: {sub_keyword}")
                i += 1 if sub_keyword is None else 2
            else:
                # Skip invalid names like 'SeleniumLibrary .'
                i += 2 if sub_keyword else 1
            continue

        # --- Documentation Block ---
        elif line == "Documentation:":
            doc_lines = []
            j = i + 1
            while j < len(lines) and not lines[j].startswith(("Start", "KEYWORD", "Arguments:", "TRACE", "Status:", "Message:", "TEST")):
                doc_lines.append(lines[j])
                j += 1
            documentation = ' '.join(doc_lines)
            formatted.append(f"{indent}Documentation: {documentation}")
            i = j
            continue

        # --- Arguments ---
        elif line.startswith("Arguments:"):
            formatted.append(f"{indent}Arguments: {line.replace('Arguments:', '').strip()}")
            i += 1
            continue

        # --- Timing Info ---
        elif line.startswith("Start / End"):
            formatted.append(f"{indent}Timing: {line}")
            i += 1
            continue

        else:
            i += 1

    with open(output_path, 'w',encoding="utf-8") as out:
        out.write('\n'.join(formatted))

    print(f"Formatted nested log written to {output_path}")

output_path = r"C:\Users\akumarse\Documents\Ashish\RAG_project\extracted_data\extracted_log_output.txt"
clean_robot_log_for_llm_nested(output_path,output_path)