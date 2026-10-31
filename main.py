from website import create_app
from flask import render_template

app = create_app()

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error_404.html"), 404

@app.errorhandler(405)
def page_not_found(error):
    return render_template("error_405.html"), 405

if __name__ == '__main__' :
	app.run(host='0.0.0.0', port=5000, debug=True)