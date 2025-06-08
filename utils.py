from typing import Dict, List, Any
from models import SoilTest

def validate_soil_test_data(data: Dict[str, Any]) -> List[str]:
    """Validate soil test data and return list of errors"""
    errors = []
    
    # Required fields
    if not data.get('location', '').strip():
        errors.append('Location is required')
    
    # pH validation
    try:
        ph = float(data.get('ph', 0))
        if ph < 0 or ph > 14:
            errors.append('pH must be between 0 and 14')
    except (ValueError, TypeError):
        errors.append('pH must be a valid number')
    
    # Nitrogen validation
    try:
        nitrogen = float(data.get('nitrogen', 0))
        if nitrogen < 0:
            errors.append('Nitrogen must be a positive number')
    except (ValueError, TypeError):
        errors.append('Nitrogen must be a valid number')
    
    # Phosphorus validation
    try:
        phosphorus = float(data.get('phosphorus', 0))
        if phosphorus < 0:
            errors.append('Phosphorus must be a positive number')
    except (ValueError, TypeError):
        errors.append('Phosphorus must be a valid number')
    
    # Potassium validation
    try:
        potassium = float(data.get('potassium', 0))
        if potassium < 0:
            errors.append('Potassium must be a positive number')
    except (ValueError, TypeError):
        errors.append('Potassium must be a valid number')
    
    # Latitude validation (optional)
    if data.get('latitude') is not None:
        try:
            lat = float(data['latitude'])
            if lat < -90 or lat > 90:
                errors.append('Latitude must be between -90 and 90')
        except (ValueError, TypeError):
            errors.append('Latitude must be a valid number')
    
    # Longitude validation (optional)
    if data.get('longitude') is not None:
        try:
            lng = float(data['longitude'])
            if lng < -180 or lng > 180:
                errors.append('Longitude must be between -180 and 180')
        except (ValueError, TypeError):
            errors.append('Longitude must be a valid number')
    
    return errors

def generate_fertilizer_recommendations(soil_test: SoilTest) -> Dict[str, Any]:
    """Generate fertilizer recommendations based on soil test results"""
    recommendations = {
        'overall': '',
        'ph_recommendation': '',
        'nitrogen_recommendation': '',
        'phosphorus_recommendation': '',
        'potassium_recommendation': '',
        'priority': 'medium',
        'actions': []
    }
    
    actions = []
    
    # pH Analysis and Recommendations
    if soil_test.ph < 6.0:
        recommendations['ph_recommendation'] = f"Soil is acidic (pH {soil_test.ph}). Apply lime to raise pH to 6.0-7.0 range for optimal nutrient availability."
        actions.append({
            'type': 'pH adjustment',
            'action': 'Apply agricultural lime',
            'amount': f"{calculate_lime_requirement(soil_test.ph)} lbs per 1000 sq ft",
            'priority': 'high'
        })
        recommendations['priority'] = 'high'
    elif soil_test.ph > 7.5:
        recommendations['ph_recommendation'] = f"Soil is alkaline (pH {soil_test.ph}). Apply sulfur or organic matter to lower pH."
        actions.append({
            'type': 'pH adjustment',
            'action': 'Apply elemental sulfur',
            'amount': f"{calculate_sulfur_requirement(soil_test.ph)} lbs per 1000 sq ft",
            'priority': 'high'
        })
        recommendations['priority'] = 'high'
    else:
        recommendations['ph_recommendation'] = f"pH level ({soil_test.ph}) is optimal for most crops."
    
    # Nitrogen Analysis and Recommendations
    if soil_test.nitrogen < 20:
        recommendations['nitrogen_recommendation'] = f"Low nitrogen levels ({soil_test.nitrogen} ppm). Apply nitrogen-rich fertilizer or compost."
        actions.append({
            'type': 'nitrogen',
            'action': 'Apply nitrogen fertilizer (21-0-0 or similar)',
            'amount': f"{calculate_nitrogen_requirement(soil_test.nitrogen)} lbs per 1000 sq ft",
            'priority': 'medium'
        })
    elif soil_test.nitrogen > 50:
        recommendations['nitrogen_recommendation'] = f"High nitrogen levels ({soil_test.nitrogen} ppm). Reduce nitrogen fertilization to prevent burning and runoff."
        actions.append({
            'type': 'nitrogen',
            'action': 'Reduce or skip nitrogen fertilization',
            'amount': 'Monitor and test again in 6 months',
            'priority': 'low'
        })
    else:
        recommendations['nitrogen_recommendation'] = f"Nitrogen levels ({soil_test.nitrogen} ppm) are adequate."
    
    # Phosphorus Analysis and Recommendations
    if soil_test.phosphorus < 15:
        recommendations['phosphorus_recommendation'] = f"Low phosphorus levels ({soil_test.phosphorus} ppm). Apply phosphorus fertilizer for strong root development."
        actions.append({
            'type': 'phosphorus',
            'action': 'Apply phosphorus fertilizer (0-46-0 or bone meal)',
            'amount': f"{calculate_phosphorus_requirement(soil_test.phosphorus)} lbs per 1000 sq ft",
            'priority': 'medium'
        })
    elif soil_test.phosphorus > 50:
        recommendations['phosphorus_recommendation'] = f"High phosphorus levels ({soil_test.phosphorus} ppm). Avoid phosphorus fertilizers."
        actions.append({
            'type': 'phosphorus',
            'action': 'Skip phosphorus fertilization',
            'amount': 'Use low or no-phosphorus fertilizers',
            'priority': 'low'
        })
    else:
        recommendations['phosphorus_recommendation'] = f"Phosphorus levels ({soil_test.phosphorus} ppm) are sufficient."
    
    # Potassium Analysis and Recommendations
    if soil_test.potassium < 100:
        recommendations['potassium_recommendation'] = f"Low potassium levels ({soil_test.potassium} ppm). Apply potassium fertilizer for plant health and disease resistance."
        actions.append({
            'type': 'potassium',
            'action': 'Apply potassium fertilizer (0-0-60 or potash)',
            'amount': f"{calculate_potassium_requirement(soil_test.potassium)} lbs per 1000 sq ft",
            'priority': 'medium'
        })
    elif soil_test.potassium > 300:
        recommendations['potassium_recommendation'] = f"High potassium levels ({soil_test.potassium} ppm). Reduce potassium fertilization."
        actions.append({
            'type': 'potassium',
            'action': 'Reduce potassium fertilization',
            'amount': 'Monitor levels and retest in 12 months',
            'priority': 'low'
        })
    else:
        recommendations['potassium_recommendation'] = f"Potassium levels ({soil_test.potassium} ppm) are adequate."
    
    # Overall recommendation
    high_priority_actions = [a for a in actions if a['priority'] == 'high']
    medium_priority_actions = [a for a in actions if a['priority'] == 'medium']
    
    if high_priority_actions:
        recommendations['overall'] = "Immediate attention required for soil pH adjustment. Address pH issues first, then nutrient deficiencies."
        recommendations['priority'] = 'high'
    elif medium_priority_actions:
        recommendations['overall'] = "Moderate nutrient deficiencies detected. Apply recommended fertilizers for optimal plant growth."
        recommendations['priority'] = 'medium'
    else:
        recommendations['overall'] = "Soil nutrient levels are generally good. Continue regular monitoring and maintenance."
        recommendations['priority'] = 'low'
    
    recommendations['actions'] = actions
    
    return recommendations

def calculate_lime_requirement(ph: float) -> int:
    """Calculate lime requirement based on pH"""
    if ph < 5.0:
        return 15
    elif ph < 5.5:
        return 12
    elif ph < 6.0:
        return 8
    else:
        return 5

def calculate_sulfur_requirement(ph: float) -> int:
    """Calculate sulfur requirement to lower pH"""
    if ph > 8.0:
        return 10
    elif ph > 7.5:
        return 6
    else:
        return 3

def calculate_nitrogen_requirement(nitrogen: float) -> int:
    """Calculate nitrogen fertilizer requirement"""
    if nitrogen < 10:
        return 4
    elif nitrogen < 20:
        return 2
    else:
        return 1

def calculate_phosphorus_requirement(phosphorus: float) -> int:
    """Calculate phosphorus fertilizer requirement"""
    if phosphorus < 5:
        return 3
    elif phosphorus < 15:
        return 2
    else:
        return 1

def calculate_potassium_requirement(potassium: float) -> int:
    """Calculate potassium fertilizer requirement"""
    if potassium < 50:
        return 4
    elif potassium < 100:
        return 3
    else:
        return 1

def analyze_soil_health(soil_test: SoilTest) -> Dict[str, str]:
    """Provide overall soil health analysis"""
    health_score = 0
    total_factors = 4
    
    # pH score
    if 6.0 <= soil_test.ph <= 7.0:
        health_score += 1
    elif 5.5 <= soil_test.ph <= 7.5:
        health_score += 0.7
    elif 5.0 <= soil_test.ph <= 8.0:
        health_score += 0.4
    
    # Nitrogen score
    if 20 <= soil_test.nitrogen <= 50:
        health_score += 1
    elif 15 <= soil_test.nitrogen <= 60:
        health_score += 0.7
    elif 10 <= soil_test.nitrogen <= 80:
        health_score += 0.4
    
    # Phosphorus score
    if 15 <= soil_test.phosphorus <= 50:
        health_score += 1
    elif 10 <= soil_test.phosphorus <= 60:
        health_score += 0.7
    elif 5 <= soil_test.phosphorus <= 80:
        health_score += 0.4
    
    # Potassium score
    if 100 <= soil_test.potassium <= 300:
        health_score += 1
    elif 75 <= soil_test.potassium <= 400:
        health_score += 0.7
    elif 50 <= soil_test.potassium <= 500:
        health_score += 0.4
    
    health_percentage = (health_score / total_factors) * 100
    
    if health_percentage >= 80:
        health_status = "Excellent"
        health_description = "Your soil is in excellent condition with optimal nutrient levels."
    elif health_percentage >= 60:
        health_status = "Good"
        health_description = "Your soil is in good condition with minor adjustments needed."
    elif health_percentage >= 40:
        health_status = "Fair"
        health_description = "Your soil needs some attention to improve nutrient levels."
    else:
        health_status = "Poor"
        health_description = "Your soil requires significant improvement in multiple areas."
    
    return {
        'score': round(health_percentage, 1),
        'status': health_status,
        'description': health_description
    }