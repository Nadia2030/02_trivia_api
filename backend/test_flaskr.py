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
        self.database_name = "trivia"
        self.database_path = "postgres://Nani:@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        # create a new question
        self.new_question =  {
                "question": 'What is tha captial of Saudi Arabia?',
                "answer": "Riaydh",
                "category": 1,
                "difficulty": 1
            }
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """ 
     # test get categories end point
    def test_get_categories(self):
        res = self.client().get('/categories')

        data = json.loads(res.data.decode('utf-8'))
        #ref: https://github.com/fabienvauchelles/scrapoxy-python-api/issues/5
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
    
    
    # test get categories end point if the method not allowed
    def test_post_categories_method(self):
        res = self.client().post('/categories')
        data = json.loads(res.data.decode('utf-8'))
        #ref: https://github.com/fabienvauchelles/scrapoxy-python-api/issues/5
        self.assertEqual(res.status_code,405)
        self.assertTrue(res._status,'405 METHOD NOT ALLOWED')

    # test get questions end point
    def test_get_questions(self):
        res = self.client().get('/questions')

        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
    
    # test get questions end point check the error sent when the request is for a page out of range
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=100')
        self.assertEqual(res.status_code,404)
        self.assertTrue(res._status,'404 NOT FOUND')
    
    # test the question delete end point  
    def test_delete_question(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data.decode('utf-8'))
        
        question = Question.query.filter(Question.id == 1).one_or_none()
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted_id'],4)
        self.assertEqual(question, None) 
    
    # test the question delete end point when the question that not exist 
    def test_delete_question_not_exist(self):
        res = self.client().delete('/questions/100')
        self.assertEqual(res.status_code,422)
        self.assertTrue(res._status,'422 Unprocessable Entity')
    
    # test insert question end point 
    def test_insert_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['question'])

    # test inser pouestion end point method not allowed when inser a question  
    def test_when_insert_question_not_allowed(self):
        res = self.client().post('/questions/4', json=self.new_question)
        self.assertEqual(res.status_code,405)
        
        self.assertTrue(res._status,'405 METHOD NOT ALLOWED')

    # test search end point
    def test_search_question(self):
        res = self.client().post('/search', json={'searchTerm': ""})
        data = json.loads(res.data.decode('utf-8'))
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
    # test search end point method not allowed
    def test_search_question_not_exist_search_term(self):
        res = self.client().get('/search', json={'searchTerm': ""})
        
        self.assertEqual(res.status_code,405)
        self.assertTrue(res._status,'METHOD NOT ALLOWED')
    
    # test get questions by category end point
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
         
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
    
    # test get questions by category end point if category not exist
    def test_get_questions_by_category_not_exist(self):
        res = self.client().get('/categories/100/questions')
        
        self.assertEqual(res.status_code,404)
        self.assertTrue(res._status,'404 NOT FOUND')
    
    # test quizzes end point
    def test_play_quizz(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'type':'All', 'id': 0},'previous_questions': []})
                                            
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
    
    # test quizzes end point if previous_questions object not exist
     
    def test_play_quizze_previous_questions_not_exist(self):
        res = self.client().get('/quizzes', json={'quiz_category': {'type':'All', 'id': 0}})
        
        self.assertEqual(res.status_code,405)
        self.assertTrue(res._status,'METHOD NOT ALLOWED')

    
    
    # reference: Lesson4: API Testing
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()