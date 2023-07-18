from flask import Flask, request, render_template, redirect, send_file
from PIL import Image
import os.path

# Note: static folder means all files from there will be automatically served over HTTP
app = Flask(__name__, static_folder="public")

# Define route for homepage --> "/" (index.html)
@app.route("/")
def index():
    return render_template('index.html')

# Define route for 404 - error --> "/404"
@app.route("/404")
def error():
    return render_template('404.html')

# Define route for displaying the last encoded image --> "/image/last/encoded" (encoded_image.png)
@app.route("/image/last/encoded")
def encoded():
    image = 'public/images/encoded_image.png'

    # Display the last encoded image only if it exists
    if os.path.isfile(image):
        return send_file(image, mimetype = 'image/png')
    return redirect('/404')

# Define route for displaying the last message decoded --> "/image/last/decoded"
# Note: last decoded message was saved in "message.txt" file  
@app.route("/image/last/decoded")
def decoded():
    file_path = 'public/message/message.txt'

    # Display the last decoded text only if "message.txt" was generated
    if os.path.isfile(file_path):
        # Read the contents of the text file
        with open(file_path, 'r') as file:
            text_content = file.read()
        # Return the text content as the response
        return text_content
    return redirect('/404')

# Encoding process
@app.route("/encode", methods = ['POST', 'GET'])
def encode():
    # For the encoding form, I've made a little parse 
    error_msg = ""
    succes = ""
    if request.method == "POST":
        file_format = 'PNG'
        message = request.form.get("message", "")
        files = request.files['files']
        if not message:
            return render_template("encode.html", error_msg = error_msg)
        elif not files:
            return render_template("encode.html", error_msg = error_msg)
        
        # Load the image using PIL
        img = Image.open(files)

        # If the image isn't .PNG, display error
        if img.format != file_format:
            error_msg = "Incorrect image format. Please use a .PNG"
            return render_template("encode.html", error_msg = error_msg)

        # Get width and height of the image
        width, height = img.size

        # To know where do I have to stop in decode process, I've added at the end of the
        # message the string "$#&"
        message = message + "$#&"

        # Convert message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in message)

        # Get the number of total pixels of the image
        total_pixels = width * height * 3

        # Verify if you can actually encode the message into the input image        
        if len(binary_message) > total_pixels:
            error_msg = "The image is too small to encode the message you entered."
            return render_template("encode.html", error_msg = error_msg)
        succes = "Encoding was done successfully."

        # Start encode (stop when there is no more message)
        message_stop = False
        binary_index = 0
        for i in range(width):
            if message_stop:
                break
            for j in range(height):
                if message_stop:
                    break
                # Get the red, green and blue value of the current pixel
                r, g, b, alpha = img.getpixel((i, j))
                # Verify if the current bit of message can be encoded using the formula (color & 0xFE | msg_bit)
                if binary_index < len(binary_message):
                    r = (r & 0xFE) | int(binary_message[binary_index])
                    binary_index += 1
                else:
                    message_stop = True
                if binary_index < len(binary_message):
                    g = (g & 0xFE) | int(binary_message[binary_index])
                    binary_index += 1
                else:
                    message_stop = True
                if binary_index < len(binary_message):
                    b = (b & 0xFE) | int(binary_message[binary_index])
                    binary_index += 1
                else:
                    message_stop = True
                
                # Modify current pixel
                img.putpixel((i, j), (r, g, b, alpha))
        encoded_image_path = 'public/images/encoded_image.png'

        # Save the encoded image at "public/images/encoded_image.png"
        img.save(encoded_image_path)
    return render_template('encode.html', succes = succes)

# Decoding process
@app.route("/decode", methods = ['POST', 'GET'])
def decode():
    # Small parse for the form 
    file_format = 'PNG'
    res = ""
    succes = ""
    if request.method == "POST":
        files = request.files['files']
        if not files:
            with open('public/message/message.txt', 'r') as f: 
                string = f.readline()
            res = string
            return render_template("decode.html", res = res)
        
        # Load the image using PIL
        img = Image.open(files)

        # If the image isn't .PNG, display error
        if img.format != file_format:
            error_msg = "Incorrect image format. Please use a .PNG"
            if os.path.isfile('public/message/message.txt'):
                with open('public/message/message.txt', 'r') as f: 
                    string = f.read()
                    res = string
            return render_template("decode.html", error_msg = error_msg, res = res)    
        succes = "Decoding was done successfully."
    
        # Get width and height of the image
        width, height = img.size
        
        # Start decoding 
        found_stop = False
        binary_message = ''
        for i in range(width):
            if found_stop:
                break
            for j in range(height):
                if found_stop:
                    break
                # The complementary operation of (color & 0xFE | msg_bit) is (color & 1)
                r, g, b, alpha = img.getpixel((i, j))
                binary_message += format(r & 1, 'b')
                binary_message += format(g & 1, 'b')
                binary_message += format(b & 1, 'b')
                # If the end string is found ($#&), then the loop stops
                if binary_message.endswith('001001000010001100100110'):
                    found_stop = True

        # Convert binary to ASCII string using chunks of 8 bits
        decoded_message = bytearray(int(binary_message[i:i+8], 2) for i in range(0, len(binary_message), 8)).decode(errors='ignore')

        # Now, I will find the string I've added in the encoding process and save only the message that was encoded
        position = decoded_message.find("$#&")
        result = decoded_message[:position]

        # Save the message into a .txt file
        with open('public/message/message.txt', 'w') as f: 
            f.write(str(result))
    if os.path.isfile('public/message/message.txt'):
        with open('public/message/message.txt', 'r') as f: 
            string = f.read()
            res = string
    return render_template('decode.html', res = res, succes = succes)

# Run the webserver 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

