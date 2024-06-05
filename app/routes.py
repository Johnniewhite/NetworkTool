from flask import Blueprint, render_template, jsonify, current_app
from . import utils
import threading
import asyncio

bp = Blueprint('main', __name__)

data = {}
data_lock = threading.Lock()

async def update_data():
    global data
    with data_lock:
        data = await asyncio.to_thread(utils.run_network_tests)

@bp.route('/')
async def dashboard():
    """
    Render the dashboard with network test results.
    """
    await update_data()
    return render_template('dashboard.html', data=data)

@bp.route('/api/test')
async def api_test():
    """
    API endpoint to run network tests and return results as JSON.
    """
    results = await asyncio.to_thread(utils.run_network_tests)
    return jsonify(results)
