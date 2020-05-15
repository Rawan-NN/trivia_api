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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
        res=self.client().get('/categories')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])

    def test_404_when_get_wrong_endpoint_categories(self):
        res=self.client().get('/categorie')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Not found')

    def test_get_questions(self):
        res=self.client().get('/questions?page=1')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])
       
    def test_404_when_get_wrong_endpoint(self):
        res=self.client().get('/question?page=1')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Not found')

    def test_delete_question(self):
        res=self.client().delete('/questions/20')
        data=json.loads(res.data)
        question=Question.query.filter(Question.id==20).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(question,None)

    def test_404_when_delete_id_does_not_exist(self):
        res=self.client().delete('/questions/200')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Not found')

    def test_create_question(self):
        res=self.client().post('questions/new-question',json=Question("whats the sum of 2 +1?","3","1",1).format())
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
       
    def test_422_when_missing_json_body(self):
        res=self.client().post('questions/new-question',json={})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data["message"],"unprocessable")
       
    def test_search_question(self):
        res=self.client().post('/questions/search',json={'searchTerm':"sum"})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
       
    def test_404_when_serachTerm_not_in_body(self):
        res=self.client().post('/questions/search',json={})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'unprocessable')

    def test_get_questions_based_on_category(self):
        res=self.client().get('/questions/categories/1')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
       
    def test_when_category_not_found(self):
        res=self.client().get('/questions/categories/988')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"Not found")
    
    def test_quizzes(self):
        q_data={"previous_questions":[],
        "quiz_category":{"type": "Geography", 
        "id": 3}
        }
        res=self.client().post('/quizzes',json=q_data)
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
       
       
    def test_404_if_not_found(self):
        q_data={"previous_questions":[],
        "quiz_category":{"type": "technology", 
        "id": 70}
        }
        res=self.client().post('/quizzes/1',json=q_data)
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data["message"],"Not found")
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()