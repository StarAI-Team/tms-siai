import joblib

# Load the model file
model_content = joblib.load("traffic_model.pkl")

# Print the type and contents of the file
print("type",type(model_content))
print("model",model_content)
