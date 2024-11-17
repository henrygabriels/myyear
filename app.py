# app.py
from flask import Flask, render_template, jsonify
import random
import os
import re

app = Flask(__name__)

def txt_to_sentences(txt_path):
    """Extract sentences from a TXT file, removing quotation marks and excluding sentences with specific titles."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Define excluded terms
        excluded_terms = ['Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Rev.']
        
        # Replace excluded terms with a unique marker to avoid selecting these sentences
        for term in excluded_terms:
            text = text.replace(term, 'EXCLUDED_TERM')
        
        # Use regex to split sentences, preserving terminal punctuation
        sentences = re.findall(r'[^.!?]+[.!?]', text)
        
        # Define a regex pattern to remove various types of quotation marks
        quote_pattern = r'[“”"\'‘’]'

        # Filter and clean sentences
        cleaned_sentences = []
        for s in sentences:
            # Remove leading and trailing whitespace
            s = s.strip()
            
            # Remove all quotation marks (both single and double quotes, including curly quotes)
            s = re.sub(quote_pattern, '', s)
            
            # Check other conditions
            if (len(s) > 20 and len(s.split()) > 5 
                and 'EXCLUDED_TERM' not in s):
                cleaned_sentences.append(s)
        
        print(f"Successfully loaded {len(cleaned_sentences)} sentences from {txt_path}")
        return cleaned_sentences
    except FileNotFoundError:
        print(f"Error: File not found - {txt_path}")
        return []
    except Exception as e:
        print(f"Error loading {txt_path}: {str(e)}")
        return []

# Load and process the books at startup
current_dir = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(current_dir, 'books')

book1_path = os.path.join(books_dir, 'Moshfegh_-Ottessa-My-Year-of-Rest-and-Relaxation.txt')
book2_path = os.path.join(books_dir, 'Kang_-Han-The-Vegetarian.txt')

print(f"Attempting to load book1 from: {book1_path}")
print(f"Attempting to load book2 from: {book2_path}")

BOOK1_SENTENCES = txt_to_sentences(book1_path)
BOOK2_SENTENCES = txt_to_sentences(book2_path)

if not BOOK1_SENTENCES:
    BOOK1_SENTENCES = ["Error loading first TXT file. Please ensure the file exists in the 'books' folder."]
if not BOOK2_SENTENCES:
    BOOK2_SENTENCES = ["Error loading second TXT file. Please ensure the file exists in the 'books' folder."]

# Keep track of used sentences to avoid repetition
used_sentences = {
    'book1': set(),
    'book2': set()
}

def get_random_sentence(book_sentences, book_key):
    """Get a random unused sentence, resetting if all sentences have been used."""
    available_sentences = set(book_sentences) - used_sentences[book_key]
    
    if not available_sentences:
        used_sentences[book_key].clear()
        available_sentences = set(book_sentences)
    
    sentence = random.choice(list(available_sentences))
    used_sentences[book_key].add(sentence)
    return sentence

current_book = 'book1'  # Start with book1

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_sentence')
def get_sentence():
    global current_book
    if current_book == 'book1':
        sentence = get_random_sentence(BOOK1_SENTENCES, 'book1')
        current_book = 'book2'
    else:
        sentence = get_random_sentence(BOOK2_SENTENCES, 'book2')
        current_book = 'book1'
    
    return jsonify({
        'sentence': sentence,
        'book': current_book
    })

@app.route('/restart')
def restart():
    # Clear the used sentences sets
    used_sentences['book1'].clear()
    used_sentences['book2'].clear()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
