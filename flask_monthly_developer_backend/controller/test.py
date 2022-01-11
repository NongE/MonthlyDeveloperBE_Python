import jwt

from flask import request
from datetime import datetime, timedelta

from flask_restx import fields, Namespace, Resource

from config.env import Env

from .controller_decorator import validate_token_decorator
authorizations = {
        'jwt_token': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'header'
        },
        'test_token': {
            'type': 'apiKey',
            'in': 'header',
            'name': Env.TEST_TOKEN_NAME
        },
        'query_exam': {
            'type': 'apiKey',
            'in': 'query',
            'name': 'code'
        }
    }
test_ns = Namespace("TEST API", description="동작 테스트를 위한 API",
                    authorizations=authorizations)

validate_jwt = test_ns.parser()
validate_jwt.add_argument('header', location='headers')


@test_ns.route('/get_validate_token', methods=['GET'])
class GetValidateToken(Resource):
    @test_ns.doc(security = "jwt_header")
    @validate_token_decorator
    def get(self):
        return {"result": "validate Header/Token"}

@test_ns.route('/post_validate_token', methods=['POST'])
class PostValidateToken(Resource):
    @test_ns.doc(security = "jwt_header")
    @validate_token_decorator
    def post(self):
        return {"result": "post method validate Header/Token"}

@test_ns.route('/issue_token', methods=['GET'])
class IssueToken(Resource):
    @test_ns.doc(security = "test_token")
    def get(self):
        
        try:
            if request.headers["test_header"] == Env.TEST_TOKEN:
                payload = {
                        "iss": "test_api",
                        "sub": "test_id",
                        "userId": "test_user_name",
                        "exp": datetime.utcnow() + timedelta(seconds=Env.ACCESS_TOKEN_EXPIRED_TIME)
                }

                created_token = jwt.encode(payload, Env.TEST_SECRET_KEY , Env.TEST_ALGORITHM)

                return created_token
            else:
                return "Invalidate Token"
        except:
            return "Not Found Test Token"