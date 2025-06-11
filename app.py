from flask import Flask, render_template, request, redirect
import json
import os
import time
import secrets
import base64

app = Flask(__name__)

# ---------- Utility Functions ----------
def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            if filename.endswith('.txt'):
                f.write('[]' if 'subscribers' in filename else '{}')
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# ---------- Task Functions ----------
def load_tasks():
    return load_json('tasks.txt')

def save_tasks(tasks):
    save_json('tasks.txt', tasks)

def add_task(name):
    tasks = load_tasks()
    if any(task['name'].lower() == name.lower() for task in tasks):
        return False
    tasks.append({
        "id": secrets.token_hex(4),
        "name": name,
        "completed": False
    })
    save_tasks(tasks)
    return True

# ---------- Email Subscription ----------
def subscribe_email(email):
    subscribers = load_json('subscribers.txt')
    if email in subscribers:
        return "already"

    pending = load_json('pending_subscriptions.txt')
    code = str(secrets.randbelow(1000000)).zfill(6)
    pending[email] = {"code": code, "timestamp": int(time.time())}
    save_json('pending_subscriptions.txt', pending)

    return code

def verify_email(email, code):
    pending = load_json('pending_subscriptions.txt')
    if email in pending and pending[email]['code'] == code:
        subscribers = load_json('subscribers.txt')
        subscribers.append(email)
        save_json('subscribers.txt', subscribers)
        del pending[email]
        save_json('pending_subscriptions.txt', pending)
        return True
    return False

# ---------- Routes ----------


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_name = request.form.get('task_name')
        if task_name:
            added = add_task(task_name)
            if not added:
                print("⚠️ Task already exists.")
        return redirect('/')
    
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/toggle/<task_id>', methods=['POST'])
def toggle_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    save_tasks(tasks)
    return redirect('/')

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks(tasks)
    return redirect('/')


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if not email:
        return redirect('/')

    code = subscribe_email(email)
    
    # In real app, you'd send this link via email
    verify_link = f"http://localhost:5000/verify?email={email}&code={code}"

    tasks = load_tasks()
    return render_template('index.html', tasks=tasks, verify_link=verify_link)

    
@app.route('/verify')
def verify():
    email = request.args.get('email')
    code = request.args.get('code')

    if email and code and verify_email(email, code):
        return render_template('verify.html', success=True)
    else:
        return render_template('verify.html', success=False)



@app.route('/unsubscribe')
def unsubscribe():
    encoded_email = request.args.get('email')
    if not encoded_email:
        return render_template("unsubscribe.html", success=False)

    try:
        email = base64.urlsafe_b64decode(encoded_email).decode()
        subscribers = load_json('subscribers.txt')
        if email in subscribers:
            subscribers.remove(email)
            save_json('subscribers.txt', subscribers)
            return render_template("unsubscribe.html", success=True)
    except Exception:
        pass

    return render_template("unsubscribe.html", success=False)



if __name__ == "__main__":
    app.run(debug=True)
