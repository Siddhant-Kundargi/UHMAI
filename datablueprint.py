from flask import Blueprint, jsonify

data_bp = Blueprint('data', __name__)

@data_bp.route('/process', methods=['POST'])
def process_data():
    # Add data processing logic here
    return jsonify({"message": "Data processed"})
