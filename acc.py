import os
from flask import Flask, request, session, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.secret_key = '025896314785368236'
# Sample user database
users_db = {
    "john.doe@example.com": {
        "name": "Lee Doe",
        "password": generate_password_hash("password123"),
        "email": "john.doe@example.com",
        "phone": "+123456789",
        "address": "123 Main Street, City, Country",
        "profile_picture": "user-profile.jpg",
        "email_notifications": "enabled",
        "sms_notifications": "enabled",
        "profile_visibility": "public",
        "share_data": "no",
    }
}

def get_user_by_email(email):
    return users_db.get(email)

# Set up the upload folder (not used for MinIO, but keeping it for other potential uses)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve the user account page
@app.route('/')
def user_account():
    email = session.get('email', 'john.doe@example.com')
    user = users_db.get(email)
    return render_template('account.html', user=user)

# Route to update profile information
@app.route('/update-profile', methods=['POST'])
def update_profile():
    email = session.get('email', 'john.doe@example.com')
    user = users_db.get(email)
    
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        profile_picture = request.files.get('profile_picture')  # Use .get to avoid KeyError

        # Save profile picture to MinIO 
        if profile_picture and profile_picture.filename:
            try:
                files = {'file': (profile_picture.filename, profile_picture.stream, profile_picture.mimetype)}
                response = requests.post('http://localhost:6000/upload-file', files=files)
                
                if response.status_code == 200:
                    user['profile_picture'] = response.text  # Get the file URI from MinIO response
                else:
                    flash(f"Failed to upload profile picture: {response.text}", "error")
                    return redirect(url_for('user_account'))
            except Exception as e:
                flash(f"Error uploading profile picture: {str(e)}", "error")
                return redirect(url_for('user_account'))

        # Update other details
        user['name'] = name
        user['phone'] = phone
        user['address'] = address
        flash("Profile updated successfully!", "success")
    
    return redirect(url_for('user_account'))

# Route to change password
@app.route('/update-password', methods=['POST'])
def update_password():
    email = session.get('email', 'john.doe@example.com')
    user = users_db.get(email)
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')  # Use .get() to avoid KeyError
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for('user_account'))

        # Check current password
        if not check_password_hash(user['password'], current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for('user_account'))
        
        # Check if new password matches confirm password
        if new_password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for('user_account'))
        
        # Update password
        user['password'] = generate_password_hash(new_password)
        flash("Password updated successfully!", "success")
    
    return redirect(url_for('user_account'))


@app.route('/privacy_settings', methods=['POST'])
def privacy_settings():
    email = request.form.get('email')  # Get the email from the form (use session in real app)
    profile_visibility = request.form.get('profile_visibility')
    share_data = request.form.get('share_data', 'yes')  # Default to 'yes'

    # Get the user by email
    user = get_user_by_email(email)

    if user:
        # Update the user's privacy settings
        user['profile_visibility'] = profile_visibility
        user['share_data'] = share_data
        flash('Privacy settings updated successfully!')
    else:
        flash('User not found.')

    return redirect(url_for('user_account'))

# Route to handle settings update
"""@app.route('/update-settings', methods=['POST'])
def update_settings():
    email = session.get('email', 'john.doe@example.com')
    
    privacy_settings = request.form.get('privacy_settings')
    notification_settings = request.form.get('notification_settings')
    

    flash("Settings updated successfully!", "success")
    
    return redirect(url_for('user_account')) """

@app.route('/notification_settings', methods=['POST'])
def notification_settings():
    email = request.form.get('email')  # Get the email from the form (use session in real app)
    email_notifications = request.form.get('email_notifications', 'enabled')  # Default to 'enabled'
    sms_notifications = request.form.get('sms_notifications', 'enabled')  # Default to 'enabled'

    # Get the user by email
    user = get_user_by_email(email)

    if user:
        # Update the user's notification settings
        user['email_notifications'] = email_notifications
        user['sms_notifications'] = sms_notifications
        flash('Notification settings updated successfully!')
    else:
        flash('User not found.')

    return redirect(url_for('user_account'))


# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug = True, port=7000)



