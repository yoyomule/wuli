from flask import Flask, render_template, jsonify, request
import math

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # 获取前端传来的参数
    data = request.get_json()
    focal_length = float(data['focal_length'])
    object_distance = float(data['object_distance'])
    object_height = float(data['object_height'])
    
    # 计算成像
    if object_distance != focal_length:
        # 计算像距
        image_distance = (focal_length * object_distance) / (object_distance - focal_length)
        # 计算像高
        image_height = -(image_distance * object_height) / object_distance
        
        return jsonify({
            'success': True,
            'image_distance': image_distance,
            'image_height': image_height,
            'is_virtual': object_distance < focal_length
        })
    else:
        return jsonify({
            'success': False,
            'message': '当物距等于焦距时，像在无穷远处'
        })

if __name__ == '__main__':
    app.run(debug=True) 