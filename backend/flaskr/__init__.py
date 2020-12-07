import os
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    Set up CORS. Allow '*' for origins.
    '''
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    after_request decorator used to set Access-Control-Allow
    '''
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    An endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        try:
            # Get all catogries and order them by type
            categories = Category.query.all()
            # check if the query has results
            # if not, send not found (error code) to the front end
            if categories is None:
                abort(404)
            # we need the resulting object to be JSON serializable
            # using for loop we conver it to a json fomat

            all_categories = {}
            for category in categories:
                all_categories[category.id] = category.type
                print(all_categories[category.id])

            # return the results to the fornt end

            print(all_categories)

            return jsonify({
              'success': True,
              'categories': all_categories
            })
        except Exception as e:
            abort(e)

    '''
    including pagination (every 10 questions)
    and store the current page questions in a list
    '''

    def paginate_questions(request, selections):
        try:
            # get the value of the key request (page)
            # if not exist defualt to one
            page = request.args.get('page', 1, type=int)
            # specify the start index of the questions
            start = (page - 1) * QUESTIONS_PER_PAGE
            # specify the end index of of the questions
            end = start + QUESTIONS_PER_PAGE
            questions = [selection.format() for selection in selections]
            # send only the group of questions in this page
            current_question = questions[start:end]
            if len(current_question) == 0:
                abort(404)
        except Exception as e:
            abort(e)

        return current_question
    '''
    An endpoint to handle GET/POST requests for questions,
    - If te request is a GET request:
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    '''
    @app.route('/questions')
    def get_questions():
        try:
            # Get all questions
            questions = Question.query.all()
            # if not, send not found (error code) to the front end
            if len(questions) == 0:
                abort(404)
            else:
                # get the current group of questions on the page
                current_questions = paginate_questions(request, questions)

                # get the catogries
                categories = get_categories().get_json()['categories']
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions),
                    'categories': categories,
                    'currentCategory': None
                })
        except Exception as e:
            abort(e)

    '''
    This endpoint POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    '''
    @app.route('/questions', methods=['POST'])
    def insert_question():
        try:
            body = request.get_json()
            # Get the question data form the user request
            new_question = body.get('question', None)
            print(new_question)
            new_answer = body.get('answer', None)
            new_category = body.get("category", None)
            new_difficulty = body.get("difficulty", None)
            # insert the data in to Question table
            question = Question(question=new_question, answer=new_answer,
                                category=new_category,
                                difficulty=new_difficulty)
            question.insert()
            # based on the front end,
            # the following info need to be send in the response
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)
            current_category = body.get("category", None)
            # reference: Lesson3: Endpoints and Payloads
            return jsonify({
                'success': True,
                'question': current_question,
                'total_questions': len(selection),
                'current_category': current_category
            })
        except Exception as e:
            abort(e)

    '''
    An endpoint to DELETE question using a question ID.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # get the question with the id attached to the client request
            question = Question.query.get(question_id)
            # if not, send not found (error code) to the front end
            if question is None:
                abort(422)
            # delete the question and return the results to the front end
            question.delete()
            return jsonify({
                'success': True,
                'deleted_id': question_id
            })
        except Exception as e:
            abort(e)

    '''
    A POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    '''
    @app.route('/search', methods=['POST'])
    def search_questions():
        # get the search term from the user request

        try:
            search_term = request.get_json()['searchTerm']
            print(search_term)

            # send a query to search for the questions
            # that include the search term
            selections = Question.query.filter(Question.question.ilike(
                    '%' + search_term + '%')).all()
            print(selections)
            # reference :
            # https://stackoverflow.com/questions/20363836/postgresql-ilike-query-with-sqlalchemy
            formatted_questions = [
                  selection.format() for selection in selections
              ]
            print(formatted_questions)
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': None
            })
        except Exception as e:
            abort(e)
    '''
    A GET endpoint to get questions based on category.
    '''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            # get all questions based on the category id
            selections = Question.query.filter_by(category=category_id).all()
            print(selections)
            # if not, send not found (error code) to the front end
            if len(selections) == 0:
                abort(404)
            formatted_questions = [
              selection.format()
              for selection in selections]
            current_category = {}
            # get all catogries as json format
            categories = get_categories().get_json()['categories']
            # search the json respone using catogry id
            for i in categories:
                if i == category_id:
                    print("*"+i)
                    print("**"+categories[i])
                    current_category[i] == categories[i]
                    break
            # reference: https://linuxhint.com/search_json_python/

            print(current_category)
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(selections),
                'current_category': current_category
            })
        except Exception as e:
            abort(e)

    '''
    A POST endpoint to get questions to play the quiz.
    This endpoint  take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            # get the quiz category
            category = int(request.get_json()['quiz_category']['id'])
            print(category)
            # get the list of questions based on catogrey
            # if the user select all (catogry id = 0 )
            # we will return all questions
            questions = {}
            if category is 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=category).all()

            print(questions)
            # get the list of the previous questions so we won't repeat them
            previous_questions = request.get_json()['previous_questions']
            print(previous_questions)

            current_question = ''
            # return the first question in the list
            # that it is not in te previous questions
            for question in questions:
                if question.id not in previous_questions:
                    current_question = question
                    break
            print(current_question)
            return jsonify({
                'success': True,
                'question': current_question.format()
                })
        except Exception as e:
            abort(e)

    '''
    Error handlers for all expected errors
    '''
    # reference: Lesson3: Endpoints and Payloads
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "Bad Request"
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "method not allowed"
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': "an internal server error"
        }), 500

    return app
