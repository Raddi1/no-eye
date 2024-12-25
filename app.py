
# app.py
import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'chat.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        data = request.json
        new_message = Message(content=data['content'])
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"id": new_message.id, "content": new_message.content, "timestamp": new_message.timestamp}), 201

    # GET request
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    return jsonify([{"id": msg.id, "content": msg.content, "timestamp": msg.timestamp} for msg in messages])

@app.route('/admin/update_message/<int:message_id>', methods=['POST'])
def admin_update_message(message_id):
    admin_key = request.headers.get('Admin-Key')
    if admin_key != 'your_secret_key':  # Replace 'your_secret_key' with your actual key
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    new_content = data.get('content')
    if not new_content:
        return jsonify({"error": "Content is required"}), 400

    message = Message.query.get(message_id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    message.content = new_content
    db.session.commit()

    return jsonify({"success": True, "message": "Message updated"})

if __name__ == '__main__':
    app.run(debug=True)
