from flask import Flask, request, jsonify
import textrazor
import json
from difflib import SequenceMatcher

textrazor.api_key = "148e07b6094bfd5b58eb169c49b0407475c3a374bd017a6dd0c213d6"
client = textrazor.TextRazor(extractors=["entities", "topics"])

app = Flask(__name__)

# Load base keywords from a file
with open("base_keywords.txt", "r", encoding="utf-8") as base_file:
    base_keywords = set(line.strip().lower() for line in base_file)

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def filter_generated_keywords(keywords):
    filtered_keywords = set()  # Use a set to store unique keywords
    for keyword in keywords:
        add_keyword = True
        for base_keyword in filtered_keywords.copy():
            similarity_score = similarity(keyword, base_keyword)
            if similarity_score >= 0.8:
                # Keep the keyword with greater length
                if len(keyword) > len(base_keyword):
                    filtered_keywords.remove(base_keyword)
                else:
                    add_keyword = False
                    break

        if add_keyword:
            filtered_keywords.add(keyword)

    return list(filtered_keywords)

def filter_base_keywords(generated_keywords):
    filtered_base_keywords = []
    for base_keyword in base_keywords:
        for generated_keyword in generated_keywords:
            similarity_score = similarity(generated_keyword.lower(), base_keyword)
            if similarity_score >= 0.8:
                filtered_base_keywords.append(generated_keyword)
                break  # Move to the next base keyword
    return filtered_base_keywords

@app.route("/", methods=["POST"])
def home():
    if request.method == "POST":
        try:
            data = request.get_json(force=True)
            text = data["text"]
        except KeyError:
            return jsonify({"error": "Invalid request format. Make sure to provide 'text' in the request payload."}), 400

        response = client.analyze(text)
        generated_keywords = [entity.id.lower() for entity in response.entities()]

        filtered_generated_keywords = filter_generated_keywords(generated_keywords)
        filtered_base_keywords = filter_base_keywords(filtered_generated_keywords)

        print(filtered_base_keywords)
        
        result = list(set(filtered_base_keywords))
        
        return jsonify({"keywords": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
