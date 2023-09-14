from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app import db
from flask_login import current_user, login_required
from models import Course, Category, User, Reviews
from tools import CoursesFilter, ImageSaver
import math

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSE_PARAMS = [
    'author_id', 'name', 'category_id', 'short_desc', 'full_desc'
]

def params():
    return { p: request.form.get(p) for p in COURSE_PARAMS }

def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': [x for x in request.args.getlist('category_ids') if x],
    }

@bp.route('/')
def index():
    courses = CoursesFilter(**search_params()).perform()
    pagination = db.paginate(courses)
    courses = pagination.items
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template('courses/index.html',
                           courses=courses,
                           categories=categories,
                           pagination=pagination,
                           search_params=search_params())

@bp.route('/new')
def new():
    categories = db.session.execute(db.select(Category)).scalars()
    users = db.session.execute(db.select(User)).scalars()
    return render_template('courses/new.html',
                           categories=categories,
                           users=users)

@bp.route('/create', methods=['POST'])
def create():

    f = request.files.get('background_img')
    if f and f.filename:
        img = ImageSaver(f).save()

    course = Course(**params(), background_image_id=img.id)
    db.session.add(course)
    db.session.commit()

    flash(f'Курс {course.name} был успешно добавлен!', 'success')

    return redirect(url_for('courses.index'))

@bp.route('/<int:course_id>')
def show(course_id):
    course = db.get_or_404(Course, course_id)
    reviews = Reviews.query.filter(Reviews.course_id == course_id).order_by(Reviews.created_at.desc()).limit(5).all()
    is_review = Reviews.query.filter(Reviews.user_id == current_user.id).all()
    return render_template('courses/show.html', course=course, reviews = reviews, is_review = is_review) # is_review = False

@bp.route('/<int:course_id>/create_review', methods=["POST"])
@login_required
def create_review(course_id):
    course = db.get_or_404(Course, course_id)
    reviews = Reviews.query.filter(Reviews.course_id == course_id).order_by(Reviews.created_at.desc()).limit(5).all()
    is_review = Reviews.query.filter(Reviews.user_id == current_user.id).all()
    rating = request.form.get("rating")
    text = request.form.get("text")
    if not text:
        error = "Введите коментарий отзыва"
        flash('Ошибка ввода параметров.', 'danger')
        return render_template('courses/show.html', course=course, reviews = reviews, rating = rating, error = error, is_review = is_review)
    
    try:
        course.rating_sum = course.rating_sum + int(rating)
        course.rating_num += 1
        db.session.commit()

        new_reviews = Reviews(
            rating = rating,
            text = text,
            course_id = course_id,
            user_id = current_user.id
        )
        db.session.add(new_reviews)
        db.session.commit()
        flash("Отзыв успешно добавлен.", "success")  
    except:
        flash("При добавлении отзыва возникла ошибка.", "danger")
        db.session.rollback()
    
    return redirect('/courses/' + str(course_id))

@bp.route('/<int:course_id>/show_reviews', methods=["POST", "GET"])
def show_reviews(course_id):
    course = db.get_or_404(Course, course_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config["PER_PAGE"]
    page_count = math.ceil(Reviews.query.filter(Reviews.course_id == course_id).count() / per_page)

    sort_type = request.args.get('sort_type', "1", type=str)

    if request.method == "POST":
        sort_type = request.form.get('sort')

    if sort_type == "1":
        reviews = Reviews.query.filter(Reviews.course_id == course_id).order_by(Reviews.created_at.desc()).limit(per_page).offset(per_page * (page - 1)).all()
    elif sort_type == "2":
        reviews = Reviews.query.filter(Reviews.course_id == course_id).order_by(Reviews.rating.desc()).limit(per_page).offset(per_page * (page - 1)).all()
    elif sort_type == "3":
        reviews = Reviews.query.filter(Reviews.course_id == course_id).order_by(Reviews.rating).limit(per_page).offset(per_page * (page - 1)).all()
    
    

    return render_template('courses/reviews.html', course=course, reviews=reviews, page=page, page_count=page_count, sort_type=sort_type)