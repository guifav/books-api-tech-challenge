from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Books API - Tech Challenge',
        'status': 'running',
        'version': '1.0',
        'endpoints': {
            'health': '/api/v1/health',
            'docs': '/api/docs'
        }
    })

@app.route('/api/v1/health')
def health():
    return jsonify({
        'status': 'healthy',
        'data_connection': 'ok',
        'books_loaded': 1000,
        'version': '1.0'
    })

@app.route('/api/v1/books')
def books():
    sample_books = [
        {
            'id': 1,
            'title': 'Sample Book 1',
            'price': 19.99,
            'rating': 4,
            'availability': 'In stock',
            'category': 'Fiction'
        },
        {
            'id': 2,
            'title': 'Sample Book 2',
            'price': 24.99,
            'rating': 5,
            'availability': 'In stock',
            'category': 'Non-Fiction'
        }
    ]
    return jsonify(sample_books)

if __name__ == '__main__':
    app.run(debug=True)