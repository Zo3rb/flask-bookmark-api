from flask import jsonify, redirect

from src import create_app, db
from src.bookmark.bookmark_model import Bookmark
from src.constants import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

app = create_app()

@app.route('/health_check')
def health_check():

    """
        an Endpoint to health check the API.
    """

    return jsonify({'message': "API is Running without Problems"}), HTTP_200_OK

@app.route('/<short_url>')
def handle_visit(short_url):

    """
        an Endpoint to redirect to the original url
        from "domain/short_link".
        Args:
            short_url (str): the shorted link to redirect to its original.
    """

    bookmark = Bookmark.query.filter_by(short_url=short_url).first()
    if not bookmark:
        return jsonify({'error': 'Not Found'}), HTTP_404_NOT_FOUND
        
    bookmark.visits += 1
    db.session.commit()
    return redirect(bookmark.url)

@app.errorhandler(HTTP_404_NOT_FOUND)
def handle_404(e):

    """
        an Endpoint to handle Not Found Errors.
        Args:
            e (object): the Error Object
    """

    return jsonify({'Error': "Not Found"}), HTTP_404_NOT_FOUND

@app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
def handle_404(e):

    """
        an Endpoint to handle Internal Server Errors.
        Args:
            e (object): the Error Object
    """

    return jsonify({'Error': "Something Went Wrong"}), HTTP_500_INTERNAL_SERVER_ERROR

if __name__ == '__main__':
    app.run(debug=True)