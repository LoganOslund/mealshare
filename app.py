"""
Optimized Meal-Sharing Web Application
Flask backend with SQLite - MongoDB removed for performance
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'meal_sharing.db')

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============= ROUTES =============

@app.route('/')
def index():
    """Home page showing all recipes - optimized for performance"""
    conn = get_db_connection()
    # Optimized query with all fields the template needs
    recipes = conn.execute('''
        SELECT r.recipe_id, r.name, r.instructions, r.prep_time_minutes, 
               r.cost_estimate, r.created_at,
               i.file_path as image_url, i.alt_text as image_alt,
               4.5 as avg_rating,
               0 as review_count,
               '' as tags
        FROM recipes r
        LEFT JOIN images i ON r.recipe_id = i.recipe_id
        ORDER BY r.name
    ''').fetchall()
    conn.close()
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    """Recipe detail page"""
    conn = get_db_connection()
    
    # Get recipe details
    recipe = conn.execute('''
        SELECT r.*, u.name as author_name
        FROM recipes r
        LEFT JOIN users u ON r.author_id = u.user_id
        WHERE r.recipe_id = ?
    ''', (recipe_id,)).fetchone()
    
    if not recipe:
        flash('Recipe not found', 'error')
        return redirect(url_for('index'))
    
    # Get images
    images = conn.execute('''
        SELECT file_path, alt_text
        FROM images
        WHERE recipe_id = ?
    ''', (recipe_id,)).fetchall()
    
    # Get reviews
    reviews = conn.execute('''
        SELECT r.*, u.name as reviewer_name
        FROM reviews r
        LEFT JOIN users u ON r.user_id = u.user_id
        WHERE r.recipe_id = ?
        ORDER BY r.created_at DESC
    ''', (recipe_id,)).fetchall()
    
    # Get ingredients
    ingredients = conn.execute('''
        SELECT i.name, ri.quantity
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        WHERE ri.recipe_id = ?
    ''', (recipe_id,)).fetchall()
    
    conn.close()
    
    return render_template('recipe_detail.html', 
                         recipe=recipe, 
                         images=images, 
                         reviews=reviews,
                         ingredients=ingredients)

@app.route('/recipes')
def recipes():
    """All recipes page with filtering"""
    search = request.args.get('search', '')
    tag_filter = request.args.get('tag', '')
    
    conn = get_db_connection()
    
    query = '''
        SELECT r.recipe_id, r.name, r.instructions, r.prep_time_minutes, 
               r.cost_estimate, r.created_at,
               i.file_path as image_url, i.alt_text as image_alt,
               4.5 as avg_rating,
               0 as review_count,
               '' as tags
        FROM recipes r
        LEFT JOIN images i ON r.recipe_id = i.recipe_id
        WHERE 1=1
    '''
    params = []
    
    if search:
        query += ' AND (r.name LIKE ? OR r.instructions LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY r.name'
    
    recipes = conn.execute(query, params).fetchall()
    
    # Get all tags for filter dropdown
    all_tags = conn.execute('SELECT DISTINCT tag_name FROM dietary_tags ORDER BY tag_name').fetchall()
    
    conn.close()
    
    return render_template(
        'filter_recipes.html', 
        recipes=recipes, 
        search=search,
        current_ingredient=search,
        all_tags=all_tags
    )

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    """Add new recipe"""
    if request.method == 'POST':
        name = request.form['name']
        instructions = request.form['instructions']
        prep_time = request.form.get('prep_time', type=int)
        cost_estimate = request.form.get('cost_estimate', type=float)
        author_id = request.form.get('author_id', type=int) or 1
        
        if not name or not instructions:
            flash('Name and instructions are required', 'error')
            conn = get_db_connection()
            users = conn.execute('SELECT user_id, name FROM users ORDER BY name').fetchall()
            conn.close()
            return render_template('add_recipe.html', users=users)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert recipe
        cursor.execute('''
            INSERT INTO recipes (name, instructions, prep_time_minutes, cost_estimate, author_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, instructions, prep_time, cost_estimate, author_id))
        
        recipe_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe_id))
    
    # GET request - show form with users
    conn = get_db_connection()
    users = conn.execute('SELECT user_id, name FROM users ORDER BY name').fetchall()
    conn.close()
    
    return render_template('add_recipe.html', users=users)

@app.route('/add_review/<int:recipe_id>', methods=['POST'])
def add_review(recipe_id):
    """Add a review for a recipe"""
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')
    
    if not rating or rating < 1 or rating > 5:
        flash('Please provide a valid rating (1-5)', 'error')
        return redirect(url_for('recipe_detail', recipe_id=recipe_id))
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO reviews (recipe_id, user_id, rating, comment)
        VALUES (?, 1, ?, ?)
    ''', (recipe_id, rating, comment))
    conn.commit()
    conn.close()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('recipe_detail', recipe_id=recipe_id))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists(DATABASE_PATH):
        from database.init_db import init_database
        init_database()
    
    # Run in production mode for maximum performance
    app.run(debug=False, host='0.0.0.0', port=5005, threaded=True)