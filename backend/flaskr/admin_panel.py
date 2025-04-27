import json
from flask import Blueprint, request, render_template, Response
from flaskr.db_project import db, User, Painting
from flaskr.content import get_paint
from http import HTTPStatus
from flask_jwt_extended import create_access_token,  create_refresh_token, get_jwt_identity, jwt_required


art_bp = Blueprint('admin', __name__, url_prefix='/dev.dudorov.com/api/gallery/admin')

@art_bp.get('')
@jwt_required()
def get_admin_panel():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return Response(
            json.dumps({
                "success": False,
                "error": "User not found"
            }),
            HTTPStatus.NOT_FOUND,
            mimetype="application/json",
        )
    paintings_all = db.session.query(Painting).all()
    paintings_list = [
        {'id': row.id, 'size': row.size, 'price': row.price, 'status': row.status, 'search_query': row.search_query} for
        row in paintings_all]
    response = Response(
        json.dumps(
            {
                "success": True,
                "status": 200,
                "data": {
                    "id": [paint['id'] for paint in paintings_list],
                }
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@art_bp.post('/paintings')
@jwt_required()
def add_paint():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return Response(
            json.dumps({
                "success": False,
                "error": "User not found"
            }),
            HTTPStatus.NOT_FOUND,
            mimetype="application/json",
        )
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'data' not in data:
            return Response(
                json.dumps({"error": "Invalid input"}),
                HTTPStatus.BAD_REQUEST,
                mimetype="application/json"
            )
        painting_data = data['data'].get('painting', {})
        required_fields = ['title', 'status', 'price', 'body', 'size', 'search_query', 'image']
        for field in required_fields:
            if field not in painting_data:
                return Response(
                    json.dumps({"error": f"Missing field: {field}"}),
                    HTTPStatus.BAD_REQUEST,
                    mimetype="application/json"
                )
        existing_painting = db.session.query(Painting).filter(Painting.title == painting_data['title']).first()
        if existing_painting:
            return Response(
                json.dumps({"error": f"A painting called {painting_data['title']} already exists."}),
                HTTPStatus.BAD_REQUEST,
                mimetype="application/json"
            )
        try:
            new_painting = Painting(title=painting_data['title'],
                                    status=painting_data['status'],
                                    price=painting_data['price'],
                                    body=painting_data['body'],
                                    size=painting_data['size'],
                                    user_id=user.id,
                                    search_query=painting_data['search_query'],
                                    image=painting_data['image'])
            db.session.add(new_painting)
            db.session.commit()
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
                mimetype="application/json"
            )
        painting = db.session.query(Painting).filter(Painting.title == painting_data['title']).first()
        response = Response(
            json.dumps(
                {
                    "success": True,
                    "status": 200,
                    "data": {
                        "id": painting.id,
                        "title": painting.title
                    }}
            ),
            HTTPStatus.OK,
            mimetype="application/json",
        )
        return response
    return render_template('forms.html')


@art_bp.put('/paintings/<int:paint_id>')
@jwt_required()
def update_paint(paint_id):
    paint = get_paint(paint_id)
    if not paint:
        return Response(
            json.dumps({"error": "Painting not found"}),
            HTTPStatus.NOT_FOUND,
            mimetype="application/json"
        )
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return Response(
            json.dumps({
                "success": False,
                "error": "User not found"
            }),
            HTTPStatus.NOT_FOUND,
            mimetype="application/json",
        )

    data = request.get_json()
    if not data or 'data' not in data:
        return Response(
            json.dumps({"error": "Invalid input"}),
            HTTPStatus.BAD_REQUEST,
            mimetype="application/json"
        )
    painting_data = data['data'].get('painting', {})
    required_fields = ['title', 'status', 'price', 'body', 'size']
    for field in required_fields:
        if field not in painting_data:
            return Response(
                json.dumps({"error": f"Missing field: {field}"}),
                HTTPStatus.BAD_REQUEST,
                mimetype="application/json"
            )
    try:
        for key, value in painting_data.items():
            setattr(paint, key, value)
        db.session.commit()
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json"
        )
    finally:
        db.session.close()

    info_paint = get_paint(paint_id)
    response = Response(
        json.dumps(
            {
                "success": True,
                "status": 200,
                "data": {
                    "id": paint_id,
                    "painting": {
                        "title": info_paint.title,
                        "body": info_paint.body,
                        "status": info_paint.status,
                        "size": info_paint.size,
                        "price": float(info_paint.price),
                        "search_query": info_paint.search_query,
                        "created_at": info_paint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "updated_at": info_paint.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "image": info_paint.image,
                    },
                }, }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


