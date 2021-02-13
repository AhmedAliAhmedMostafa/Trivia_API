import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format("ahmed",'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        '''Test getting all the categories.'''
        response = self.client().get('/categories').json

        categories = [category.format() for category in Category.query.order_by('id').all()]
        categories_formatted = {str(tuple(category.values())[0]):str(tuple(category.values())[1]) for category in categories }

        self.assertEqual(response['success'], True)
        self.assertEqual(response['categories'], categories_formatted)
    
    def test_get_all_questions_second_page(self):
        '''Test getting all the questions in the second page.'''
        response = self.client().get('/questions?page=2').json

        page_questions = Question.query.paginate(2, 10, False)
        page_questions = [page.format() for page in page_questions.items]
        total_questions = len(Question.query.all())

        self.assertEqual(response['success'], True)
        self.assertEqual(response['questions'], page_questions)
        self.assertEqual(response['total_questions'], total_questions)
        self.assertEqual(response['current_category'], "All")
    
    def test_get_unbound_page(self):
        '''Test getting the questions in out of range page '''
        response = self.client().get('/questions?page=2000').json

        self.assertNotEqual(response['success'], True)
        self.assertEqual(response['code'], 404)
        self.assertEqual(response['message'], "Resource Not Found.")
    
    def test_delete_question(self):
        '''Test delete question with id 5.'''
        response = self.client().delete('/questions/5').json
        question = Question.query.get(5)

        self.assertEqual(response['success'], True)
        self.assertIsNone(question)

    def test_delete_inexistent_question(self):
        '''Test delete ineistent question with id 5000 '''
        response = self.client().delete('/questions/5000').json
        

        self.assertEqual(response['success'], False)
        self.assertEqual(response['code'], 404)
        self.assertEqual(response['message'], "Resource Not Found.")

    def test_post_new_question(self):
        '''Test posting a new question.'''
        request_body = json.dumps({
            "question":"What is the capital of Egypt?",
            "answer":"Cairo",
            "difficulty":3,
            "category":3,
        })
        response = self.client().post('/questions', data=request_body, content_type='application/json')
        new_question = Question.query.get(response.json['id'])

        self.assertEqual(response.json['success'], True)
        self.assertEqual(new_question.question, "What is the capital of Egypt?")
        self.assertEqual(new_question.answer, "Cairo")
        self.assertEqual(new_question.difficulty, 3)
        self.assertEqual(new_question.category, 3)

    def test_post_new_question_with_missing_attribute(self):
        '''Test Post new question with missing question attribute.'''

        request_body = json.dumps({
            "answer":"China",
            "difficulty":2,
            "category":1,
        })
        response = self.client().post('/questions', data=request_body, content_type='application/json')

        self.assertEqual(response.json['success'], False)
        self.assertEqual(response.json['code'], 400)
        self.assertEqual(response.json['message'], "Bad Request.")

    def test_search_for_question(self):
        '''Test Searching for all the questions that contain title'''
        response = self.client().post('/questions', json={"searchTerm":"title"}).json
        matching_questions = Question.query.filter(Question.question.ilike("%{}%".format('title'))).paginate(1, 10, False).items
        matching_questions = [question.format() for question in matching_questions]

        self.assertEqual(response['success'], True)
        self.assertEqual(response['questions'],  matching_questions)

    def test_search_for_question_with_no_body(self):
        ''' Test making a POST requestto /questions without any body.''' 
        response = self.client().post('/questions')


        self.assertEqual(response.json['success'], False)
        self.assertEqual(response.json['code'], 400)
        self.assertEqual(response.json['message'], "Bad Request.")

    def test_getting_question_by_category(self):
        '''Test getting questions that belong to the Science category'''
        response = self.client().get('/categories/1/questions').json
        questions = [question.format()for question in Question.query.filter_by(category=1).all()]

        self.assertEqual(response['success'], True)
        self.assertEqual(response['questions'], questions)
        self.assertTrue(response.get('total_questions'))
        self.assertEqual(response.get('current_category'),"Science")
    
    def test_getting_questions_of_inexistent_category(self):
        '''Test getting questions of inexistent category'''
        response = self.client().get('/categories/1000/questions').json

        self.assertEqual(response['success'], False)
        self.assertEqual(response['code'], 404)
        self.assertEqual(response['message'], "Resource Not Found.")

    def test_getting_questions_for_quiz(self):
        '''Test getting random quesion in Science category.'''
        science_question = Question.query.filter_by(category=1).first()
        response = self.client().post('/quizzes',json={
            "previous_questions":[science_question.id],
            "quiz_category":{
                "id":1,
                "Type":"Science"
            }
        }) .json
        self.assertEqual(response['success'], True)
        self.assertNotEqual(response['question'], science_question.format())
        self.assertEqual(response['question']['category'], 1)

    def test_getting_questions_for_quiz_with_malformed_request(self):
        '''Test getting random quesion with malformed body.'''
        response = self.client().post('/quizzes',json={
            "previous_questions":[1]
        }) .json
        self.assertEqual(response['success'], False)
        self.assertEqual(response['code'], 400)
        self.assertEqual(response['message'], "Bad Request.")







        

        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()