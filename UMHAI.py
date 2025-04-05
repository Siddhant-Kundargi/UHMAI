from flask import Flask, render_template
from VM import VM_bp
from datablueprint import data_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(VM_bp, url_prefix='/vm')
app.register_blueprint(data_bp, url_prefix='/data')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)