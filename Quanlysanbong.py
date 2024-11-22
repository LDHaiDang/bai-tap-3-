from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database connection parameters
db_name = 'quan_ly_san_bong'
user = 'postgres'
password = '29042004'
host = 'localhost'
port = '5432'

# Database connection
def get_db_connection():
    connection = psycopg2.connect(
        dbname=db_name,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return connection

# Home page showing statistics
@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM bookings")
    result = cursor.fetchone()
    total_bookings = result[0] if result[0] is not None else 0
    total_amount = result[1] if result[1] is not None else 0
    
    cursor.execute("SELECT customer_name, field_number, amount FROM bookings")
    bookings = cursor.fetchall()
    
    # Ensure bookings is always a list (even if empty)
    if bookings is None:
        bookings = []
    
    cursor.close()
    connection.close()
    
    return render_template('index.html', total_amount=total_amount, total_bookings=total_bookings, bookings=bookings)


# Add booking
@app.route('/add_booking', methods=['POST'])
def add_booking():
    customer_name = request.form['customer_name']
    field_number = request.form['field_number']
    amount = request.form['amount']
    
    if not customer_name or not field_number or not amount:
        flash("Vui lòng nhập đầy đủ thông tin!")
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("INSERT INTO bookings (customer_name, field_number, amount) VALUES (%s, %s, %s)",
                       (customer_name, field_number, amount))
        connection.commit()
        flash("Đặt sân thành công!")
    except Exception as e:
        flash(f"Lỗi khi thêm đơn đặt sân: {e}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('index'))

# Update booking
@app.route('/update_booking', methods=['POST'])
def update_booking():
    search_name = request.form['search_name']
    new_name = request.form['new_name']
    new_field_number = request.form['new_field_number']
    new_amount = request.form['new_amount']

    if not search_name or not new_name or not new_field_number or not new_amount:
        flash("Vui lòng nhập đầy đủ thông tin!")
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("UPDATE bookings SET customer_name = %s, field_number = %s, amount = %s WHERE customer_name = %s",
                       (new_name, new_field_number, new_amount, search_name))
        connection.commit()
        flash("Cập nhật thông tin thành công!")
    except Exception as e:
        flash(f"Lỗi khi cập nhật thông tin: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('index'))

# Delete booking
@app.route('/delete_booking', methods=['POST'])
def delete_booking():
    search_name = request.form['search_name']

    if not search_name:
        flash("Vui lòng nhập tên khách hàng để xóa!")
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM bookings WHERE customer_name = %s", (search_name,))
        connection.commit()
        flash("Xóa khách hàng thành công!")
    except Exception as e:
        flash(f"Lỗi khi xóa khách hàng: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('index'))

# Find customer
@app.route('/find_customer', methods=['POST'])
def find_customer():
    find_name = request.form['find_name']  # Lấy tên khách hàng từ form

    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT customer_name, field_number, amount FROM bookings WHERE customer_name = %s", (find_name,))
    customer = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if customer:
        return render_template('index.html', customer=customer, total_amount=None, total_bookings=None, bookings=None)
    else:
        flash("Không tìm thấy khách hàng.")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
