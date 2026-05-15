"""
Student Performance Predictor - Main Flask Application
Python 3.10 Compatible
"""

from flask import Flask, render_template, request, jsonify, session, send_file, Blueprint
from flask_login import login_required, current_user
import numpy as np
import pickle
import os
from datetime import datetime
from export_utils import create_excel_export, create_pdf_export, generate_filename
from flask_wtf.csrf import CSRFProtect

# Import models and auth
from models import db, User, Prediction, ModelMetric, init_db, get_user_predictions
from auth import init_auth, auth_bp, role_required

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Database configuration
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "predictions.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Initialize authentication
init_auth(app)

# Register main blueprint
main_bp = Blueprint('main', __name__)

# Load trained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)
print("Model loaded: model.pkl")


@main_bp.route('/')
def home():
    """Home page with prediction form"""
    return render_template('index.html')


@main_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    """Make prediction and save to database"""
    try:
        # Get form data
        student_name = request.form['student_name']

        # Validate student name - only letters and spaces allowed
        if not student_name.replace(' ', '').isalpha():
            return jsonify({'error': 'Student name must contain only letters and spaces'})

        attendance = float(request.form['attendance'])
        assignment_score = float(request.form['assignment_score'])
        internal_marks = float(request.form['internal_marks'])

        # Validate input
        if not (0 <= attendance <= 100):
            return jsonify({'error': 'Attendance must be between 0 and 100'})

        if not (0 <= assignment_score <= 20):
            return jsonify({'error': 'Assignment score must be between 0 and 20'})

        if not (0 <= internal_marks <= 30):
            return jsonify({'error': 'Internal marks must be between 0 and 30'})

        # Make prediction
        features = np.array([[attendance, assignment_score, internal_marks]])
        predicted_marks = model.predict(features)[0]
        predicted_marks = max(0, min(100, predicted_marks))
        rounded_pred = round(predicted_marks, 2)

        # Determine grade
        if predicted_marks >= 90:
            grade = 'A+'
        elif predicted_marks >= 80:
            grade = 'A'
        elif predicted_marks >= 70:
            grade = 'B'
        elif predicted_marks >= 60:
            grade = 'C'
        elif predicted_marks >= 50:
            grade = 'D'
        else:
            grade = 'F'

        # Determine performance category
        if predicted_marks >= 80:
            performance = 'Excellent'
        elif predicted_marks >= 60:
            performance = 'Good'
        elif predicted_marks >= 40:
            performance = 'Average'
        else:
            performance = 'Needs Improvement'

        # Save to database
        prediction = Prediction(
            student_name=student_name,
            attendance=attendance,
            assignment_score=assignment_score,
            internal_marks=internal_marks,
            predicted_marks=rounded_pred,
            grade=grade,
            performance=performance,
            model_used='Linear Regression',
            user_id=current_user.id
        )
        db.session.add(prediction)
        db.session.commit()

        return jsonify({
            'student_name': student_name,
            'predicted_marks': rounded_pred,
            'grade': grade,
            'performance': performance,
            'model_used': 'Linear Regression',
            'success': True
        })

    except ValueError as e:
        return jsonify({'error': 'Please enter valid numeric values'})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})


@main_bp.route('/history')
@login_required
def history():
    """View prediction history"""
    # Get predictions based on user role
    include_all = request.args.get('all', 'false').lower() == 'true'
    
    if include_all and current_user.can_view_all_predictions():
        # Teachers/Admins can view all predictions
        predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    else:
        # Students only see their own
        predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    
    data = [p.to_dict() for p in predictions]
    return render_template('history.html', history=data, show_all_option=current_user.can_view_all_predictions())


@main_bp.route('/clear-history', methods=['POST'])
@login_required
def clear_history():
    """Clear prediction history"""
    try:
        if current_user.can_view_all_predictions():
            # Admin/Teacher: clear all history
            Prediction.query.delete()
        else:
            # Student: clear only own history
            Prediction.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        return {"success": True, "message": "History cleared successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@main_bp.route('/delete-entry/<int:prediction_id>', methods=['POST'])
@login_required
def delete_entry(prediction_id):
    """Delete a specific prediction entry"""
    try:
        prediction = Prediction.query.get_or_404(prediction_id)
        
        # Check permission
        if prediction.user_id != current_user.id and not current_user.can_view_all_predictions():
            return {"success": False, "message": "Permission denied"}
        
        db.session.delete(prediction)
        db.session.commit()

        return {"success": True, "message": "Entry deleted successfully"}

    except Exception as e:
        return {"success": False, "message": str(e)}


@main_bp.route('/export/excel')
@login_required
def export_excel():
    """Export prediction history to Excel"""
    try:
        # Get predictions based on user role
        if current_user.can_view_all_predictions():
            predictions = Prediction.query.all()
        else:
            predictions = Prediction.query.filter_by(user_id=current_user.id).all()
        
        history_data = [p.to_dict() for p in predictions]

        if not history_data:
            return {"success": False, "message": "No data to export"}

        excel_file = create_excel_export(history_data)
        filename = generate_filename("xlsx")

        return send_file(
            excel_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return {"success": False, "message": f"Excel export failed: {str(e)}"}


@main_bp.route('/export/pdf')
@login_required
def export_pdf():
    """Export prediction history to PDF"""
    try:
        # Get predictions based on user role
        if current_user.can_view_all_predictions():
            predictions = Prediction.query.all()
        else:
            predictions = Prediction.query.filter_by(user_id=current_user.id).all()
        
        history_data = [p.to_dict() for p in predictions]

        if not history_data:
            return {"success": False, "message": "No data to export"}

        pdf_file = create_pdf_export(history_data)
        filename = generate_filename("pdf")

        return send_file(
            pdf_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return {"success": False, "message": f"PDF export failed: {str(e)}"}


@main_bp.route('/api/model-info')
def model_info():
    """Get model information and feature importance"""
    if hasattr(model, 'coef_'):
        coefficients = model.coef_.tolist()
        intercept = model.intercept_
        feature_names = ['Attendance (%)', 'Assignment Score', 'Internal Marks']

        feature_importance = list(zip(feature_names, coefficients))
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)

        return jsonify({
            'feature_importance': feature_importance,
            'intercept': intercept,
            'model_type': 'Linear Regression'
        })
    else:
        return jsonify({'error': 'Model not available'})


@main_bp.route('/dashboard')
@login_required
@role_required('teacher', 'admin')
def dashboard():
    """Analytics dashboard for teachers and admins"""
    return render_template('dashboard.html')


@main_bp.route('/api/analytics')
@login_required
@role_required('teacher', 'admin')
def api_analytics():
    """Get analytics data for charts"""
    try:
        # Get all predictions
        predictions = Prediction.query.all()
        
        if not predictions:
            return jsonify({
                'score_distribution': [],
                'grade_distribution': {},
                'performance_distribution': {},
                'total_predictions': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0
            })
        
        data = [p.to_dict() for p in predictions]
        
        # Score distribution (histogram bins)
        scores = [p['predicted_marks'] for p in data]
        bins = [0, 20, 40, 60, 80, 100]
        bin_labels = ['0-20', '21-40', '41-60', '61-80', '81-100']
        score_dist = [0] * 5
        for score in scores:
            for i in range(5):
                if bins[i] <= score <= bins[i+1]:
                    score_dist[i] += 1
                    break
        
        # Grade distribution
        grades = {}
        for p in data:
            grade = p['grade']
            grades[grade] = grades.get(grade, 0) + 1
        
        # Performance distribution
        perf_dist = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Needs Improvement': 0}
        for p in data:
            perf = p['performance']
            if perf in perf_dist:
                perf_dist[perf] += 1
        
        # Attendance vs Marks for scatter plot
        attendance_data = [{'x': p['attendance'], 'y': p['predicted_marks']} for p in data]
        
        return jsonify({
            'score_distribution': {'labels': bin_labels, 'data': score_dist},
            'grade_distribution': grades,
            'performance_distribution': perf_dist,
            'attendance_vs_marks': attendance_data,
            'total_predictions': len(data),
            'average_score': round(sum(scores) / len(scores), 2),
            'highest_score': max(scores),
            'lowest_score': min(scores)
        })
    except Exception as e:
        return jsonify({'error': str(e)})


# Register main blueprint
app.register_blueprint(main_bp)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
