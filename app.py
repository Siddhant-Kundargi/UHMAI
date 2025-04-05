from flask import Flask, render_template
from VM import vm_blueprint
from shared_state import initialize_physical_machines

app = Flask(__name__)

# Configure physical machines
app.config['PHYSICAL_MACHINES'] = {
    'pve': {"cpu": 4, "ram": 8192}  # RAM in MB
}

# Initialize shared state
initialize_physical_machines(app.config)

app.register_blueprint(vm_blueprint, url_prefix='/vm')

@app.route('/')
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)