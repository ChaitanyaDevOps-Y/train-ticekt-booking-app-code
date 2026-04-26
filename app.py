from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'irctc-secret-key-2024')

# Mock database for trains
trains_db = {
    '12345': {
        'number': '12345',
        'name': 'Shatabdi Express',
        'from': 'Delhi',
        'to': 'Mumbai',
        'departure': '06:00 AM',
        'arrival': '02:00 PM',
        'duration': '8h',
        'classes': {
            '1A': {'price': 2500, 'available': 45},
            '2A': {'price': 1500, 'available': 60},
            '3A': {'price': 1000, 'available': 80},
            'SL': {'price': 500, 'available': 120}
        }
    },
    '12346': {
        'number': '12346',
        'name': 'Rajdhani Express',
        'from': 'Delhi',
        'to': 'Kolkata',
        'departure': '04:30 PM',
        'arrival': '10:00 AM',
        'duration': '17h 30m',
        'classes': {
            '1A': {'price': 3500, 'available': 35},
            '2A': {'price': 2200, 'available': 50},
            '3A': {'price': 1500, 'available': 70}
        }
    },
    '12347': {
        'number': '12347',
        'name': 'Duronto Express',
        'from': 'Mumbai',
        'to': 'Delhi',
        'departure': '09:00 PM',
        'arrival': '07:00 AM',
        'duration': '10h',
        'classes': {
            '1A': {'price': 2800, 'available': 40},
            '2A': {'price': 1800, 'available': 55},
            '3A': {'price': 1200, 'available': 90},
            'SL': {'price': 600, 'available': 150}
        }
    },
    '12348': {
        'number': '12348',
        'name': 'Chennai Express',
        'from': 'Chennai',
        'to': 'Bangalore',
        'departure': '07:00 AM',
        'arrival': '12:00 PM',
        'duration': '5h',
        'classes': {
            '2A': {'price': 800, 'available': 70},
            '3A': {'price': 550, 'available': 100},
            'SL': {'price': 300, 'available': 200}
        }
    },
    '12349': {
        'number': '12349',
        'name': 'Howrah Express',
        'from': 'Howrah',
        'to': 'Delhi',
        'departure': '08:00 PM',
        'arrival': '06:00 AM',
        'duration': '10h',
        'classes': {
            '1A': {'price': 3000, 'available': 30},
            '2A': {'price': 2000, 'available': 45},
            '3A': {'price': 1300, 'available': 75},
            'SL': {'price': 550, 'available': 180}
        }
    }
}

# Store bookings (in memory - would be database in production)
bookings_db = []
booking_counter = 1000

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_trains():
    from_station = request.form.get('from')
    to_station = request.form.get('to')
    date = request.form.get('date')
    class_type = request.form.get('class')
    
    # Search for trains
    available_trains = []
    for train_num, train in trains_db.items():
        if train['from'].lower() == from_station.lower() and train['to'].lower() == to_station.lower():
            if class_type in train['classes']:
                available_trains.append({
                    'number': train['number'],
                    'name': train['name'],
                    'from': train['from'],
                    'to': train['to'],
                    'departure': train['departure'],
                    'arrival': train['arrival'],
                    'duration': train['duration'],
                    'class': class_type,
                    'price': train['classes'][class_type]['price'],
                    'available': train['classes'][class_type]['available']
                })
    
    return render_template('search_results.html', trains=available_trains, 
                         from_station=from_station, to_station=to_station, 
                         date=date, class_type=class_type)

@app.route('/book/<train_number>/<class_type>/<price>')
def book(train_number, class_type, price):
    if train_number not in trains_db:
        return redirect(url_for('home'))
    
    train = trains_db[train_number]
    if class_type not in train['classes']:
        return redirect(url_for('home'))
    
    return render_template('booking.html', train=train, class_type=class_type, 
                         price=price, max_passengers=min(6, train['classes'][class_type]['available']))

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    global booking_counter
    
    train_number = request.form.get('train_number')
    train_name = request.form.get('train_name')
    class_type = request.form.get('class_type')
    price = int(request.form.get('price'))
    passenger_count = int(request.form.get('passenger_count'))
    total_amount = price * passenger_count
    
    # Passenger details
    passengers = []
    for i in range(passenger_count):
        passenger = {
            'name': request.form.get(f'passenger_name_{i}'),
            'age': request.form.get(f'passenger_age_{i}'),
            'gender': request.form.get(f'passenger_gender_{i}')
        }
        passengers.append(passenger)
    
    # Create booking
    booking = {
        'pnr': f"PNR{booking_counter}",
        'train_number': train_number,
        'train_name': train_name,
        'class': class_type,
        'passengers': passengers,
        'total_amount': total_amount,
        'booking_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'journey_date': request.form.get('journey_date'),
        'status': 'Confirmed'
    }
    
    bookings_db.append(booking)
    booking_counter += 1
    
    # Update available seats (in real app, would update database)
    trains_db[train_number]['classes'][class_type]['available'] -= passenger_count
    
    return render_template('confirmation.html', booking=booking)

@app.route('/cancel_booking/<pnr>')
def cancel_booking(pnr):
    global bookings_db
    bookings_db = [b for b in bookings_db if b['pnr'] != pnr]
    return redirect(url_for('home'))

@app.route('/check_pnr', methods=['POST'])
def check_pnr():
    pnr = request.form.get('pnr')
    booking = None
    for b in bookings_db:
        if b['pnr'] == pnr:
            booking = b
            break
    return render_template('pnr_status.html', booking=booking, pnr=pnr)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
