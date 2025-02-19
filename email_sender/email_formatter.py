import re

def format_email_content(text):
    # Remove ##
    text = text.replace("## ", "").strip()

    # Convert bold markers (**text**) to <strong>text</strong>
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)

    # Convert italic markers (_text_) to <em>text</em>
    text = re.sub(r"_(.*?)_", r"<em>\1</em>", text)

    # Convert new lines to HTML <br> tags for spacing
    text = text.replace("\n\n", "<br><br>")

    # Convert bullet points (* text) to proper HTML list items
    lines = text.split("\n")
    formatted_lines = []
    in_list = False

    for line in lines:
        if line.startswith("* "):  # If it's a bullet point
            if not in_list:
                formatted_lines.append("<ul>")
                in_list = True
            formatted_lines.append(f"<li>{line[2:]}</li>")
        else:
            if in_list:
                formatted_lines.append("</ul>")
                in_list = False
            formatted_lines.append(f"<p>{line}</p>")

    if in_list:
        formatted_lines.append("</ul>")

    formatted_content = "\n".join(formatted_lines)

    # Final HTML Template
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h2 {{ color: #333; }}
            p {{ font-size: 14px; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 10px; }}
            a {{ color: #1a73e8; text-decoration: none; }}
        </style>
    </head>
    <body>
        {formatted_content}
    </body>
    </html>
    """
    
    return html_template
