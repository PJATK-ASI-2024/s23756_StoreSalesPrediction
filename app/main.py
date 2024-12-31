from flask import Flask, request, jsonify
import pickle

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Ładowanie wytrenowanego modelu
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Endpoint do przewidywań
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = [list(data.values())]
        prediction = model.predict(features)
        return jsonify({'prediction': int(prediction[0])})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Uruchomienie serwisu
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
