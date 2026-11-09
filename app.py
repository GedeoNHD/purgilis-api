import os
import json
import base64
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

app = Flask(__name__)

# La clé privée sera lue depuis les variables d'environnement de Render
PRIVATE_KEY_PEM = os.environ.get('PRIVATE_KEY', '').encode('utf-8')

@app.route('/generate_license', methods=['POST'])
def generate_license():
    try:
        data = request.json
        client_email = data.get('email', 'client@inconnu.com')

        private_key = serialization.load_pem_private_key(PRIVATE_KEY_PEM, password=None)

        license_data = {"client": client_email, "version": "PRO"}
        license_json = json.dumps(license_data).encode('utf-8')

        signature = private_key.sign(
            license_json,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        license_key = f"{base64.b64encode(license_json).decode('utf-8')}.{base64.b64encode(signature).decode('utf-8')}"
        
        return jsonify({"status": "success", "license_key": license_key})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)