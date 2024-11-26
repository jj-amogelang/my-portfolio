from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import numpy as np
import seaborn as sns
from scipy.interpolate import CubicSpline

sns.set_theme(style="darkgrid")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/control')
def control_page():
    return render_template('control.html')

@app.route('/run/<script_name>')
def run_script(script_name):
    try:
        output = subprocess.check_output(['python', f'{script_name}.py'], stderr=subprocess.STDOUT)
        return f"<pre>{output.decode('utf-8')}</pre>"
    except subprocess.CalledProcessError as e:
        return f"<pre>{e.output.decode('utf-8')}</pre>"

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    # Here you can add code to handle the form submission, such as sending an email
    # For now, we'll just return a success message
    return render_template('contact.html', success=True, name=name)

@app.route('/animations/<filename>')
def get_animation(filename):
    return send_from_directory('static/animations', filename)

def create_time_series(start, end, step):
    """Generate a time series for the animation."""
    return np.arange(start, end + step, step)


def setup_plot():
    """Set up the matplotlib plot for the animation."""
    fig = plt.figure(figsize=(16, 9), dpi=80, facecolor=(0.8, 0.8, 0.8))
    gs = gridspec.GridSpec(3, 3)
    plt.subplots_adjust(left=0.03, bottom=0.035, right=0.99, top=0.97, wspace=0.15, hspace=0.2)
    return fig, gs

def initialize_subplots(fig, gs):
    """Initialize subplots for the animation."""
    ax1 = fig.add_subplot(gs[:, 0:2], facecolor=(0.9, 0.9, 0.9))
    ax1.plot([0, 0], [0, 0.4], 'k', linewidth=20, alpha=0.5)  # base line
    return ax1

def setup_animation_axes(ax1):
    """Set up axes and lines for the main animation plot."""
    ax1.set_xlim(-20, 20)
    ax1.set_ylim(-20, 20)
    ax1.set_xlabel('meters [m]', fontsize=12)
    ax1.set_ylabel('meters [m]', fontsize=12)
    ax1.grid(True)

    joint_lines = [ax1.plot([], [], 'o-', linewidth=2, markersize=4)[0] for _ in range(3)]
    trajectory_line, = ax1.plot([], [], 'b--', linewidth=1.5)  # Distinct trajectory style

    return joint_lines, trajectory_line

@app.route('/set_trajectory', methods=['POST'])
def set_trajectory():
    data = request.get_json()
    waypoints = data.get('waypoints', [])
    if not waypoints:
        return jsonify({'error': 'No waypoints provided'}), 400

    time_series = create_time_series(0, 10, 0.02)
    trajectory_x, trajectory_y = interpolate_path(waypoints, time_series)
    
    # Store the trajectory for later use
    app.config['CURRENT_TRAJECTORY'] = {'x': trajectory_x, 'y': trajectory_y}
    return jsonify({'message': 'Trajectory updated successfully'})

@app.route('/generate_custom_animation')
def generate_custom_animation():
    trajectory = app.config.get('CURRENT_TRAJECTORY', None)
    if not trajectory:
        return jsonify({'error': 'No trajectory set'}), 400

    trajectory_x, trajectory_y = trajectory['x'], trajectory['y']
    joint_lengths = [5, 3, 5]

    fig, gs = setup_plot()
    ax1 = initialize_subplots(fig, gs)
    joint_lines, trajectory_line = setup_animation_axes(ax1)

    ani = animation.FuncAnimation(
        fig,
        animate_with_path_interpolation,
        frames=len(trajectory_x),
        fargs=(joint_lengths, joint_lines, trajectory_line, trajectory_x, trajectory_y),
        interval=20, blit=True
    )

    buffer = BytesIO()
    ani.save(buffer, writer='pillow', format='gif')
    buffer.seek(0)

    video_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return render_template('animation.html', video_base64=video_base64)

def interpolate_path(waypoints, time_series):
    """Cubic spline interpolation for smooth trajectories."""
    times = np.linspace(0, 1, len(waypoints))
    waypoints_x, waypoints_y = zip(*(waypoints))
    cs_x = CubicSpline(times, waypoints_x)
    cs_y = CubicSpline(times, waypoints_y)

    t_normalized = np.linspace(0, 1, len(time_series))
    trajectory_x = cs_x(t_normalized)
    trajectory_y = cs_y(t_normalized)
    return trajectory_x, trajectory_y

def animate_with_path_interpolation(frame, joint_lengths, joint_lines, trajectory_line, trajectory_x, trajectory_y):
    """Update function for the animation with path interpolation."""
    if frame >= len(trajectory_x):
        return joint_lines + [trajectory_line]

    end_effector_position = (trajectory_x[frame], trajectory_y[frame])
    angles = inverse_kinematics(end_effector_position, joint_lengths)
    positions = forward_kinematics(angles, joint_lengths)

    for j in range(len(joint_lines)):
        if j == 0:
            joint_lines[j].set_data([0, positions[j][0]], [0, positions[j][1]])
        else:
            joint_lines[j].set_data([positions[j-1][0], positions[j][0]], 
                                    [positions[j-1][1], positions[j][1]])

    trajectory_line.set_data(trajectory_x[:frame+1], trajectory_y[:frame+1])

    return joint_lines + [trajectory_line]

def interpolate_path(waypoints, time_series):
    """Cubic spline interpolation for smooth trajectories."""
    times = np.linspace(0, 1, len(waypoints))
    waypoints_x, waypoints_y = zip(*waypoints)
    cs_x = CubicSpline(times, waypoints_x)
    cs_y = CubicSpline(times, waypoints_y)

    t_normalized = np.linspace(0, 1, len(time_series))
    trajectory_x = cs_x(t_normalized)
    trajectory_y = cs_y(t_normalized)
    return trajectory_x, trajectory_y

def inverse_kinematics(end_effector_position, joint_lengths):
    """Calculate the joint angles for a given end effector position."""
    # This is a placeholder function. You need to implement the actual inverse kinematics calculations.
    return [0, 0, 0]

def forward_kinematics(joint_angles, joint_lengths):
    """Calculate the positions of all joints using forward kinematics."""
    x, y = 0, 0
    cumulative_angle = 0
    positions = []

    for angle, length in zip(joint_angles, joint_lengths):
        cumulative_angle += angle
        x += length * np.cos(cumulative_angle)
        y += length * np.sin(cumulative_angle)
        positions.append((x, y))

    return positions

if __name__ == '__main__':
    app.run(debug=True)