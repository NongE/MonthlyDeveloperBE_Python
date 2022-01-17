import os
from dotenv import load_dotenv

import jwt
import bcrypt

from flask import request
from datetime import datetime, timedelta

from flask_restx import fields, Namespace, Resource

from controller.controller_decorator import validate_token_decorator

load_dotenv()

authorizations = {
        'jwt_token': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'header'
        },
        'test_token': {
            'type': 'apiKey',
            'in': 'header',
            'name': os.environ.get("TEST_TOKEN_NAME")
        },
        'query_exam': {
            'type': 'apiKey',
            'in': 'query',
            'name': 'code'
        }
    }

test_ns = Namespace("TEST API", description="동작 테스트를 위한 API",
                    authorizations=authorizations)

test_header = test_ns.parser()
test_header.add_argument('header', location='headers', help= 'test header')

test_query_param = test_ns.parser()
test_query_param.add_argument('a', type=int,  help= 'test query param')

bcrypt_param = test_ns.parser()
bcrypt_param.add_argument('word', type=str)

test_model = test_ns.model('test model', {
        'test String': fields.String(description='Test String', required=True),
    })


@test_ns.route("", methods=["GET"])
class PingPongRoute(Resource):
    def get(self):
        return "Ping-Pong!"

@test_ns.route("/bcrypt", methods=["GET"])
class BcryptTest(Resource):
    @test_ns.expect(bcrypt_param)
    def get(self):
        p = request.args["word"]
        print(p)
        
        hash_p = bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt())
        print(hash_p)

        answer = "test"
        print(bcrypt.checkpw(answer.encode("utf-8"), hash_p))
        
        return "Ping-Pong!"


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


@test_ns.route('/issue_token', methods=['POST'])
class IssueToken(Resource):
    @test_ns.expect(test_header, test_query_param, test_model)
    # @test_ns.expect(test_model)
    def post(self):

        # Header
        print(request.headers)

        # Query
        print(request.args["a"])
        # print(test_query_param.parse_args())

        # Body
        print(request.json)
        
        try:
            if request.headers["header"] == os.environ.get("TEST_TOKEN"):
                payload = {
                        "iss": "test_api",
                        "sub": "test_id",
                        "userId": "test_user_name",
                        "exp": datetime.utcnow() + timedelta(seconds=int(os.environ.get("ACCESS_TOKEN_EXPIRED_TIME")))
                }

                created_token = jwt.encode(payload, os.environ.get("TEST_SECRET_KEY"), os.environ.get("TEST_ALGORITHM"))

                return created_token
            else:
                return "Invalidate Token"
        except:
            return "Not Found Test Token"