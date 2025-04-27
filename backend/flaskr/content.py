import json
from flask import Blueprint, request, Response
from flaskr.db_project import db, Painting, Exhibition, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus

bp = Blueprint('content', __name__, url_prefix='/dev.dudorov.com/api/gallery')


def get_paint(paint_id):
    paint = db.session.query(Painting).filter_by(id=paint_id).first()
    if paint is None:
        return None
    return paint


@bp.get('/document-paintsales/list')
def get_paints_sales():
    paintings_on_sale = db.session.query(Painting).filter(Painting.status == 'on sale').all()
    paintings_list = [
        {'id': row.id, 'size': row.size, 'price': row.price, 'status': row.status, 'search_query': row.search_query} for
        row in paintings_on_sale]
    response = Response(
        json.dumps(
            {
                "success": True,
                "status": 200,
                "data": {
                    "id": [paint['id'] for paint in paintings_list],
                    "size": [paint['size'] for paint in paintings_list],
                    "price": [float(paint['price']) for paint in paintings_list],
                    "status": [paint['status'] for paint in paintings_list],
                    "search_query": [paint['search_query'] for paint in paintings_list],
                }
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@bp.get('/document-painting/list')
def get_all_paints():
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


@bp.get('/document-aboutartist/inf')
def get_info_about_artist():
    pass


@bp.get('/document-painting/<int:paint_id>/detail-info')
def get_detail_paint(paint_id):
    info_paint = get_paint(paint_id)
    response = Response(
        json.dumps(
            {
                "success": True,
                "status": 200,
                "data": {
                    "id": int(info_paint.id),
                    'painting': {
                        "title": info_paint.title,
                        "body": info_paint.body,
                        "status": info_paint.status,
                        "size": info_paint.size,
                        "price": float(info_paint.price),
                        "search_query": info_paint.search_query,
                        "created_at": info_paint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "updated_at": info_paint.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "image": info_paint.image,
                    }
                }
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@bp.route('/document-painting/<int:paint_id>/create', methods=["POST"])
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



@bp.route('/document-painting/<int:paint_id>/delete', methods=["DELETE"])
@jwt_required()
def delete_painting(paint_id):
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
    try:
        db.session.delete(paint)
        db.session.commit()
        response = Response(
            json.dumps({"success": True}),
            HTTPStatus.OK,
            mimetype="application/json"
        )
        return response
    except Exception as e:
        db.session.rollback()
        return Response(
            json.dumps({"error": str(e)}),
            HTTPStatus.BAD_REQUEST,
            mimetype="application/json"
        )
    finally:
        db.session.close()


@bp.get('/document-poster/list')
def get_exhibitions():
    exhibitions_all = db.session.query(Exhibition).all()
    response = Response(
        json.dumps(
            {
                "success": True,
                "status": 200,
                "data": {
                    "current_exhibition": [ex.current_exhibition for ex in exhibitions_all],
                },
                'error': None
            }

        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response
