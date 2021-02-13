import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app, "postgres://{}@{}/{}".format('ahmed', 'localhost:5432', 'trivia'))
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*":{"origins":"*", "methods":"", "allow_headers":""}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def modify_response_headers(response):
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers','Content-Type')
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories',methods=['GET'])
  def get_categories():
      categories = [category.format() for category in Category.query.order_by('id').all()]
      categories_formatted = {tuple(category.values())[0]:tuple(category.values())[1] for category in categories }

      return jsonify({
        "success":True,
        "categories":categories_formatted
      })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route("/questions")
  def get_all_questions():
    page_number = request.args.get('page', 1,type=int)

    page_questions = Question.query.paginate(page_number, QUESTIONS_PER_PAGE, True)
    page_questions = [page.format() for page in page_questions.items]
    total_questions = len(Question.query.all())
    categories = [category.format() for category in Category.query.order_by('id').all()]
    categories_formatted = {tuple(category.values())[0]:tuple(category.values())[1] for category in categories }

    return jsonify({
      "success":True,
      "questions":page_questions,
      "total_questions":total_questions,
      "categories":categories_formatted,
      "current_category":"All",
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.get(id)
    if question is None:
      abort(404)
    try:
      question.delete()
      return jsonify({
        "success":True
      })
    except:
      abort(422)
    
     
  

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def post_new_question():
    data = request.get_json()
    if not data:
      abort(400)
    elif data.get('searchTerm'):
      page_number = request.args.get('page', 1)
      matching_questions = Question.query.filter(Question.question.ilike("%{}%".format(data['searchTerm']))).paginate(page_number, QUESTIONS_PER_PAGE, True).items
      total_questions = len(Question.query.all())

      return jsonify({
        "success":True,
        "questions":[question.format() for question in matching_questions],
        "total_questions":total_questions,
        "current_category":"All"
      })
    else:  
      if not data.get('question') or not data.get('answer') or not data.get('category') or not data.get('difficulty'):
        abort(400)
      new_question = Question(data['question'], data['answer'], data['difficulty'], data['category'])
      new_question.insert()

      return jsonify({
        "success":True,
        "id":new_question.id
      })
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def get_questions_by_category(id):
    current_category = Category.query.filter_by(id=id).first()
    if(current_category is None):
      abort(404)

    questions = [question.format()for question in Question.query.filter_by(category=id).all()]
    total_questions = len(Question.query.all())

    return jsonify({
      "success":True,
      "questions":questions,
      "total_questions":total_questions,
      "current_category":current_category.type
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_questions_for_quiz():
    data = request.get_json()
    if not data or not data.get('quiz_category'):
      abort(400)
    category_id = data['quiz_category']['id']
    if Category.query.get(category_id) is None and category_id!=0:
      abort(404)
    if category_id == 0:
      category_questions = Question.query.all()
    else:
      category_questions = Question.query.filter_by(category=category_id).all()
    if len(category_questions) == len(data['previous_questions']):
      return jsonify({
        "success":True,
      })
    else:
      random_question = category_questions[random.randint(0,len(category_questions)-1)]
      while random_question.id  in data['previous_questions']:
        random_question = category_questions[random.randint(0,len(category_questions)-1)]

      return jsonify({
        "success":True,
        "question":random_question.format()
      })       
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success":False,
      "code":404,
      "message":"Resource Not Found."
    }),404
  
  @app.errorhandler(422)
  def cant_process(error):
    return jsonify({
      "success":False,
      "code":422,
      "message":"Unprocessable."
    }),422
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success":False,
      "code":400,
      "message":"Bad Request."
    }),400
  return app

    