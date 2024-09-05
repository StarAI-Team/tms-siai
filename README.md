Features
•	User Authentication: Secure login and signup using Google OAuth.
•	Role-Based Views: Different interfaces for clients, transporters, and agent.
•	Real-Time Data Updates: Streamlined order processing and transporter updates.
Usage
•	Client: Sign up or log in to place orders, view order history, and update profile details.
•	Transporter: Sign up or log in to manage logistics details, view and process delivery requests.
•	Agent( Star International): View assigned deliveries and update delivery status.

Endpoints
The Flask app has the following endpoints:
Client
1. GET /transporters
•	Should return all the transporters available on the app.
•	Client can make any number of delivery  requests. Client needs to be assigned a client_id while making the request, client_id can be string/integer.
o	Should be accessed via {host}:{port}/clientapp.

2. GET / transporters /<transporter_id>
•	Returns the details for a single transporter.

3. POST /delivery_orders
•	Places a new order.





Transporter 
•	Driver app contains three tabs -
o	Waiting - Shows all the waiting request(s) that needs to be processed/rejected/accepted. Transporter can choose to process any request from here.
o	Ongoing - Shows the ongoing request(s) that have been accepted by this transporter(<transporter_id>).
o	Completed - Shows the completed request(s) that were processed by this driver(<transporter_id>).
•	It can be accessed via {host}:{port}/transporterapp?id=<transporter_id>. Where id is transporter's id & it can be string/integer.

Dashboard
•	It shows all the request(s) along with their status, driver_id, customer_id, picked_up time, request_creation_time, completion_time etc.
•	It can be accessed via {host}:{port}/dashboard.


