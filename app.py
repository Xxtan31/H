from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_migrate import Migrate
import os

app.instance_path = '/tmp/instance'
os.makedirs(app.instance_path, exist_ok=True)



app = Flask(__name__, instance_relative_config=False)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///keys.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Key modelini güncelle
class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False)
    expiration_date = db.Column(db.DateTime)
    hwid = db.Column(db.String(100), nullable=True)  # HWID kaydetmek için
    uses = db.Column(db.Integer, default=0)  # Anahtarın kaç kez kullanıldığını takip etmek için
    usage_limit = db.Column(db.Integer, default=5)  # Anahtarın kaç kez kullanılabileceğini belirlemek için

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    keys = Key.query.all()
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Key Management</title>
    <style>
        /* Global styling */
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 1200px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0px 0px 30px rgba(0, 0, 0, 0.15);
            border-radius: 12px;
        }

        /* Main Title Styling */
        .header-frame {
            text-align: center;
            position: relative;
            margin-bottom: 40px;
        }

        .header-frame::before {
            content: '';
            display: block;
            width: 80%;
            height: 150px;
            border: 5px solid #007bff;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            border-radius: 10px;
        }

        h2 {
            position: relative;
            font-size: 36px;
            font-weight: bold;
            color: #333;
            padding: 20px 40px;
            background-color: #fff;
            z-index: 1;
            display: inline-block;
        }

        /* Panel sections */
        .panel {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }

        .panel-section {
            width: 48%;
            padding: 30px;
            border-radius: 12px;
            background-color: #f9f9f9;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .panel-section:hover {
            transform: translateY(-5px);
        }

        .panel-section h3 {
            font-size: 26px;
            color: #555;
            margin-bottom: 20px;
            text-align: center;
        }

        /* Keys List */
        .keys-list {
            list-style: none;
            padding-left: 0;
            max-height: 300px;
            overflow-y: auto;
        }

        .keys-list li {
            padding: 15px;
            background-color: #e9ecef;
            margin-bottom: 10px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 18px;
        }

        .countdown {
            font-weight: bold;
            font-size: 16px;
            color: #ff6b6b;
        }

        /* Form and Buttons */
        .form-control {
            width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 18px;
            transition: border-color 0.3s ease;
        }

        .form-control:focus {
            border-color: #007bff;
            outline: none;
        }

        .btn {
            width: 100%;
            padding: 15px;
            background-color: #28a745;
            color: #fff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 20px;
            transition: background-color 0.3s ease;
        }

        .btn:hover {
            background-color: #218838;
        }

        .btn:active {
            background-color: #1e7e34;
        }

        /* Success Message */
        #message {
            text-align: center;
            margin-top: 20px;
            font-size: 20px;
            color: #28a745;
        }

        /* Scroll bar styling */
        .keys-list::-webkit-scrollbar {
            width: 8px;
        }

        .keys-list::-webkit-scrollbar-thumb {
            background-color: #007bff;
            border-radius: 4px;
        }

        .keys-list::-webkit-scrollbar-track {
            background-color: #f1f1f1;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section with Blue Frame -->
        <div class="header-frame">
            <h2>Key Management System</h2>
        </div>

        <!-- Panel Section for Keys and Form -->
        <div class="panel">
            <!-- Keys List Panel -->
            <div class="panel-section">
                <h3>Existing Keys</h3>
                <ul class="keys-list">
                    {% for key in keys %}
                        <li>
                            <span>{{ key.key }}</span>
                            <span class="countdown" data-expiration="{{ key.expiration_date.isoformat() }}"></span>
                        </li>
                    {% endfor %}
                </ul>
            </div>

            <!-- Add New Key Panel -->
            <div class="panel-section">
                <h3>Add New Key</h3>
                <input type="text" id="new-key" placeholder="Enter new key..." class="form-control">
                <label for="days">Days:</label>
                <input type="number" id="days" class="form-control" placeholder="0">
                <label for="hours">Hours:</label>
                <input type="number" id="hours" class="form-control" placeholder="0">
                <label for="minutes">Minutes:</label>
                <input type="number" id="minutes" class="form-control" placeholder="0">
                <button class="btn" onclick="addKey()">Add Key</button>
                <p id="message"></p>
            </div>
        </div>
    </div>

    <!-- Countdown and Add Key Functionality -->
    <script>
        function addKey() {
            const newKey = document.getElementById("new-key").value;
            const days = parseInt(document.getElementById("days").value) || 0;
            const hours = parseInt(document.getElementById("hours").value) || 0;
            const minutes = parseInt(document.getElementById("minutes").value) || 0;
            const expiration_minutes = (days * 24 * 60) + (hours * 60) + minutes;

            fetch('/create_key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key: newKey, expiration_minutes: expiration_minutes })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("message").textContent = data.message;
                if (data.message === 'Key created successfully') {
                    const expirationDate = new Date(Date.now() + expiration_minutes * 60000);
                    const newKeyElement = document.createElement("li");
                    newKeyElement.innerHTML = `<span>${newKey}</span> - <span class="countdown" data-expiration="${expirationDate.toISOString()}"></span>`;
                    document.querySelector(".keys-list").appendChild(newKeyElement);
                    document.getElementById("new-key").value = '';
                    document.getElementById("days").value = '';
                    document.getElementById("hours").value = '';
                    document.getElementById("minutes").value = '';
                    startCountdown();
                }
            });
        }

        function startCountdown() {
            const countdownElements = document.querySelectorAll('.countdown');
            countdownElements.forEach(function(element) {
                const expirationDate = new Date(element.getAttribute('data-expiration'));
                const parentLi = element.closest('li');
                const interval = setInterval(function() {
                    const now = new Date();
                    const timeLeft = expirationDate - now;

                    // Süresi dolmuşsa anahtarı kaldır
                    if (timeLeft <= 0) {
                        parentLi.remove(); // Süresi dolmuş anahtarları DOM'dan kaldır
                        clearInterval(interval); // Intervali durdur
                    } else {
                        const totalDays = Math.floor(timeLeft / 1000 / 60 / 60 / 24);
                        const months = Math.floor(totalDays / 30);
                        const days = totalDays % 30;
                        const hours = Math.floor(timeLeft / 1000 / 60 / 60) % 24;
                        const minutes = Math.floor(timeLeft / 1000 / 60) % 60;
                        const seconds = Math.floor(timeLeft / 1000) % 60;
                        element.innerHTML = `${months}mo ${days}d ${hours}h ${minutes}m ${seconds}s`;
                    }
                }, 1000);
            });

            // Sayfa yüklendiğinde süresi dolmuş anahtarları kontrol et
            countdownElements.forEach(function(element) {
                const expirationDate = new Date(element.getAttribute('data-expiration'));
                const now = new Date();
                if (expirationDate <= now) {
                    const parentLi = element.closest('li');
                    parentLi.remove(); // Süresi dolmuş anahtarı DOM'dan kaldır
                }
            });
        }

        // Sayfa yüklendiğinde sayfadaki tüm geri sayımları başlat
        document.addEventListener("DOMContentLoaded", function() {
            startCountdown();
        });
    </script>
</body>
</html>
    '''
    return render_template_string(html_content, keys=keys)

# Key oluşturma endpointi
@app.route('/create_key', methods=['POST'])
def create_key():
    data = request.json
    key = data.get('key')
    expiration_minutes = data.get('expiration_minutes', 60)
    expiration_date = datetime.now() + timedelta(minutes=expiration_minutes)

    if key:
        new_key = Key(key=key, expiration_date=expiration_date)
        db.session.add(new_key)
        db.session.commit()
        return jsonify({"message": "Key created successfully"}), 201
    else:
        return jsonify({"message": "Key creation failed"}), 400

# Key kullanma endpointi
@app.route('/use_key', methods=['POST'])
def use_key():
    data = request.json
    key = data.get('key')
    hwid = data.get('hwid')

    key_entry = Key.query.filter_by(key=key).first()

    if not key_entry:
        return jsonify({"message": "Key not found"}), 404

    if key_entry.hwid and key_entry.hwid != hwid:
        return jsonify({"message": "HWID does not match"}), 403

    # Anahtarın süresi dolmuş mu kontrol et
    if datetime.now() > key_entry.expiration_date:
        db.session.delete(key_entry)
        db.session.commit()
        return jsonify({"message": "Key expired and deleted"}), 403

    # Kullanım limitini kontrol et
    if key_entry.uses >= key_entry.usage_limit:
        return jsonify({"message": "Key usage limit reached"}), 403

    # Anahtar başarılı şekilde kullanıldı, kullanımları güncelle
    key_entry.uses += 1
    key_entry.hwid = hwid
    db.session.commit()

    return jsonify({"message": "Key used successfully"}), 200

# HWID kontrol endpointi
@app.route('/check_hwid', methods=['POST'])
def check_hwid():
    data = request.json
    hwid = data.get('hwid')

    key_entry = Key.query.filter_by(hwid=hwid).first()

    if not key_entry:
        return jsonify({"message": "HWID not found"}), 404

    # Süresi dolmuş mu kontrol et
    if datetime.now() > key_entry.expiration_date:
        db.session.delete(key_entry)
        db.session.commit()
        return jsonify({"message": "Key expired and deleted"}), 403

    return jsonify({"message": "HWID valid", "key": key_entry.key}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=37480, debug=True)
