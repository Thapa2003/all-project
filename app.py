from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import json
from models import SoilTest, SoilTestDB
from utils import generate_fertilizer_recommendations, validate_soil_test_data

app = Flask(__name__)
CORS(app)

# Initialize database
db = SoilTestDB()

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

# API Routes

@app.route('/api/soil-tests', methods=['GET'])
def get_soil_tests():
    """Get all soil tests"""
    try:
        tests = db.get_all_tests()
        return jsonify([test.to_dict() for test in tests])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil-tests', methods=['POST'])
def create_soil_test():
    """Create a new soil test"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = validate_soil_test_data(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Create soil test object
        soil_test = SoilTest(
            location=data['location'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            ph=float(data['ph']),
            nitrogen=float(data['nitrogen']),
            phosphorus=float(data['phosphorus']),
            potassium=float(data['potassium']),
            notes=data.get('notes', ''),
            test_date=data.get('testDate', datetime.now().strftime('%Y-%m-%d'))
        )
        
        # Save to database
        test_id = db.create_test(soil_test)
        soil_test.id = test_id
        
        # Generate recommendations
        recommendations = generate_fertilizer_recommendations(soil_test)
        
        response = soil_test.to_dict()
        response['recommendations'] = recommendations
        
        return jsonify(response), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil-tests/<int:test_id>', methods=['GET'])
def get_soil_test(test_id):
    """Get a specific soil test"""
    try:
        test = db.get_test_by_id(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        recommendations = generate_fertilizer_recommendations(test)
        response = test.to_dict()
        response['recommendations'] = recommendations
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil-tests/<int:test_id>', methods=['PUT'])
def update_soil_test(test_id):
    """Update a soil test"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = validate_soil_test_data(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Check if test exists
        existing_test = db.get_test_by_id(test_id)
        if not existing_test:
            return jsonify({'error': 'Test not found'}), 404
        
        # Update soil test
        soil_test = SoilTest(
            id=test_id,
            location=data['location'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            ph=float(data['ph']),
            nitrogen=float(data['nitrogen']),
            phosphorus=float(data['phosphorus']),
            potassium=float(data['potassium']),
            notes=data.get('notes', ''),
            test_date=data.get('testDate', existing_test.test_date)
        )
        
        db.update_test(soil_test)
        
        return jsonify(soil_test.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil-tests/<int:test_id>', methods=['DELETE'])
def delete_soil_test(test_id):
    """Delete a soil test"""
    try:
        test = db.get_test_by_id(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        db.delete_test(test_id)
        return jsonify({'message': 'Test deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil-tests/export', methods=['GET'])
def export_soil_tests():
    """Export soil tests as CSV"""
    try:
        tests = db.get_all_tests()
        
        # Create CSV content
        csv_lines = ['ID,Location,Latitude,Longitude,pH,Nitrogen (ppm),Phosphorus (ppm),Potassium (ppm),Test Date,Notes']
        
        for test in tests:
            line = f"{test.id},{test.location},{test.latitude or ''},{test.longitude or ''},{test.ph},{test.nitrogen},{test.phosphorus},{test.potassium},{test.test_date},\"{test.notes or ''}\""
            csv_lines.append(line)
        
        csv_content = '\n'.join(csv_lines)
        
        return csv_content, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=soil_tests_{datetime.now().strftime("%Y%m%d")}.csv'
        }
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/<int:test_id>', methods=['GET'])
def get_recommendations(test_id):
    """Get fertilizer recommendations for a specific test"""
    try:
        test = db.get_test_by_id(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        recommendations = generate_fertilizer_recommendations(test)
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db.test_connection() else 'disconnected'
    })

if __name__ == '__main__':
    print("Starting Soil Testing API server...")
    print("Frontend available at: http://localhost:5000")
    print("API endpoints available at: http://localhost:5000/api/*")
    app.run(debug=True, host='0.0.0.0', port=5000)