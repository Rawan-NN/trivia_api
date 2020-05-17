import os
import sys
from flask import Flask, request, abort, jsonify, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):

        response.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type,Authorization,true')

        response.headers.add(
          'Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')

        return response

    @app.route('/categories', methods=['GET']) 
    def get_categories():
      
        Category_data = Category.query.all()  # get all categories
        if not Category_data:
            abort(404)
        formatted_categories = []
        # loop through category data to get the type
        for category in Category_data:  
            formatted_categories.append(category.type.format())
        return jsonify({  # make json response
            'success': True,
            'categories': formatted_categories})
 
    @app.route('/questions', methods=['GET']) 
    def get_questions():
     
        # get all questions
        questions = Question.query.all()
        # loop through the questions to format them and append them 
        # to new array as well as cuurent categories
        if not questions:
            abort(404)

        new_questions = []
        current_category = []
        for q in questions:
            new_questions.append(
                q.format())
          
            result = db.session.query(Category.type)\
                       .filter(
                        q.category == Category.id).all()
            current_category.append(
                result)
          
        #  get all categories
        Category_data = Category.query.all()
        formatted_categories = []
        #  loop through the categories to format them 
        for category in Category_data:
            formatted_categories.append(category.type.format())

        page = request.args.get('page', type=int)
        start = (page-1)*10
        end = start+10
    
        # make json response
        return jsonify({
            'success': True,
            'questions': new_questions[start:end],
            'total_questions': len(new_questions),
            'categories': formatted_categories,
            'current_category': current_category[start:end]})
          
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):

        #  delete the question based on the id
        question = Question.query.get(question_id)
        if not question:
            abort(404)
        question.delete()
        #  make the json response
        return jsonify({
            'success': True})
              
    @app.route('/questions/new-question', methods=['POST'])
    def create_question():
        try:
            # get the question attributes
            body = request.get_json()
            new_question = body.get("question", None)
            new_answer = body.get("answer", None)
            new_category = body.get("category", None)
            new_difficulty = body.get("difficulty", None)
    
            if not new_question or not new_answer or not \
               new_category or not new_difficulty:
                abort(422)
            #  create new question and add it
            question = Question(
              new_question, new_answer, new_category, new_difficulty)
            
            question.insert()
            questions = Question.query.all()
            # get category type
            category = db.session.query(Category.type).\
                         filter(new_category == Category.id).all()
            # make the json response
            return jsonify({
                    'success': True,
                    'questions': question.format(),
                    'total_questions': len(questions),
                    'current_category': category})

        except:
            # if the proccess uncompleted because of any issue wil abort 422
            abort(422)
  
    @app.route('/questions/search', methods=['POST']) 
    def search_questions():
        try:
            #  get the search term
            body = request.get_json()      
            search_term = body.get('searchTerm', None)
            if search_term is None:
                abort(422)
            #  get the questions based on the search term
            search_result = db.session.query(Question).\
                            filter(
                              Question.question.ilike(f'%{search_term}%'))\
                              .all()
            #  loop through the questions to format them and append them 
            #  to new array as well as cuurent categories
            new_questions = []
            current_category = []
            for q in search_result:
                new_questions.append(
                    q.format())
                result = db.session.query(Category.type).\
                        filter(q.category == Category.id).all()
                current_category.append(
                    result)
      
            #  make the json response 
            return jsonify({
                    'success': True,
                    'questions': new_questions,
                    'total_questions': len(search_result),
                    'current_category': current_category})
      
        except:
            # if the proccess uncompleted because of any issue wil abort 422
            abort(422)

    @app.route('/questions/categories/<category>', methods=['GET']) 
    def get_questions_based_on_category(category):
  
        #  get the question based on the category
        questions = Question.query.filter(Question.category == category).all()
    
        if not questions:
            abort(404)
        #  loop through the questions to format them and append them 
        #  to new array as well as cuurent categories
        new_questions = []
        current_category = []
        for q in questions:
            new_questions.append(
                q.format())
      
            result = db.session.query(Category.type).\
                     filter(q.category == Category.id).all()
            current_category.append(
                result)
      
        # make the json response
        return jsonify({
            'success': True,
            'questions': new_questions,
            'total_questions': len(new_questions),
            'current_category': current_category})
      
    @app.route('/quizzes', methods=['POST']) 
    def quizzes():
        try:
            #  get the quiz category and previous_questions 
            body = request.get_json()
            previous_question = body.get("previous_questions", None)
            quiz_category = body.get("quiz_category", None)

            #  get the questions based on the category and
            #  is not on the previous questions list
            random_questions = Question.query.filter(
                                 Question.category == quiz_category["id"],
                                 Question.id.notin_(previous_question)).first()
      
            #  make json response
            return jsonify({
                'success': True,
                'question': random_questions.format()
                            if random_questions is not None else ''})
        except:
            # if the proccess uncompleted because of any issue wil abort 422
            abort(422)

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found",
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable",
          }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request",
            }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed",
            }), 405
    
    return app
