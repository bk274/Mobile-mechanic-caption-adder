from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont, ExifTags
import random
import textwrap
import os

app = Flask(__name__)

def generate_random_sentence():
    sentences = [
        "On-demand mechanics at your doorstep.",
        "Car trouble? We come to you, anywhere.",
        "Reliable mobile mechanic services for convenience.",
        "Your personal mechanic on call.",
        "Expert mobile mechanics just a call away.",
        "Car maintenance made easy, mobile service.",
        "We bring the garage to you!",
        "Need a hand? Our mobile mechanics are here.",
        "Car issues? Our skilled mechanics are ready.",
        "Relax, let our expert mechanics handle.",
        "Your car's best friend, a call away.",
        "Busy schedule? On-demand solutions tailored.",
        "Keeping your car in top shape, mobile service.",
        "We understand, your car needs love too.",
        "Wherever you are, whenever you need us.",
        "Car trouble is never convenient, but we are.",
        "Take a break, let us handle your worries.",
        "Our mobile mechanics bring expertise to you."
    ]
    return random.choice(sentences)

def calculate_multiline_textbbox(draw, font, text, max_width):
    lines = textwrap.wrap(text, width=20)
    total_height = 0
    max_line_width = 0

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        max_line_width = max(max_line_width, width)
        total_height += height

    return max_line_width, total_height

def calculate_text_color(background_color):
    r, g, b = background_color
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    text_color = (255, 255, 255) if luminance < 128 else (0, 0, 0)
    return text_color

def fix_image_orientation(image_path):
    try:
        image = Image.open(image_path)

        # Check for orientation in EXIF and rotate if necessary
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)

        # Save the fixed image
        image.save(image_path)
        image.close()

    except (AttributeError, KeyError, IndexError):
        # Cases: image doesn't have EXIF data or doesn't need rotation
        pass

def add_caption_to_image(input_image_path, output_image_path, user_caption):
    image = Image.open(input_image_path)
    image_width, image_height = image.size

    # Choose a random sentence related to mobile mechanics for the first box
    caption1 = generate_random_sentence()

    # Customize font and style for caption1
    font_size1 = int(min(image_width, image_height) * 0.06)
    flashy_font_path1 = "path/to/NovaSquare-Regular.ttf"  # Replace with the path to your downloaded TTF file
    flashy_font1 = ImageFont.truetype(font=flashy_font_path1, size=font_size1)

    # Choose random background color
    background_color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Calculate appropriate text color for the first box
    text_color1 = calculate_text_color(background_color1)

    # Wrap the text to fit within the box
    wrapped_text1 = textwrap.fill(caption1, width=16)

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Calculate the size of the text box based on the wrapped text for the first box
    text_box_width1, text_box_height1 = calculate_multiline_textbbox(draw, flashy_font1, wrapped_text1, image_width * 0.8)

    # Create a rectangle as a background for the text for the first box
    rect_width1 = text_box_width1 + 40
    rect_height1 = text_box_height1 + 70

    # Choose random position for the first text box, avoiding the center
    rect_left1 = random.uniform(0, image_width - rect_width1)
    rect_top1 = random.uniform(0, image_height - rect_height1)

    # Ensure the first box is not too close to the center
    center_margin1 = 0.2
    while abs(rect_left1 - image_width / 2) < image_width * center_margin1 and abs(
            rect_top1 - image_height / 2) < image_height * center_margin1:
        rect_left1 = random.uniform(0, image_width - rect_width1)
        rect_top1 = random.uniform(0, image_height - rect_height1)

    # Border color
    border_color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Border thickness
    border_thickness1 = 5

    # Draw the background for the first box with the chosen color
    draw.rectangle(
        [rect_left1, rect_top1, rect_left1 + rect_width1, rect_top1 + rect_height1],
        fill=background_color1
    )

    # Draw the border for the first box
    draw.rectangle(
        [rect_left1 - border_thickness1, rect_top1 - border_thickness1,
         rect_left1 + rect_width1 + border_thickness1, rect_top1 + rect_height1 + border_thickness1],
        outline=border_color1, width=border_thickness1
    )

    # Calculate the text position to center it in the first box
    text_position1 = (
        rect_left1 + (rect_width1 - text_box_width1) / 2.5,
        rect_top1 + (rect_height1 - text_box_height1) / 3
    )

    # Add the wrapped text to the image for the first box
    for line in textwrap.wrap(wrapped_text1, width=20):
        bbox1 = draw.textbbox(text_position1, line, font=flashy_font1)
        draw.text(text_position1, line, font=flashy_font1, fill=text_color1)
        text_position1 = (text_position1[0], bbox1[3])

    # Choose random background color for the second box
    background_color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Calculate appropriate text color for the second box
    text_color2 = calculate_text_color(background_color2)

    # Add the second box (user-specified caption) at a fixed position
    rect_left2 = 80
    rect_top2 = image_height - 250

    # Customize font and style for user caption
    font_size2 = int(min(image_width, image_height) * 0.06)
    flashy_font_path2 = "path/to/NovaSquare-Regular.ttf"  # Replace with the path to your downloaded TTF file
    flashy_font2 = ImageFont.truetype(font=flashy_font_path2, size=font_size2)

    # Wrap the text to fit within the box for the second box
    wrapped_text2 = textwrap.fill(user_caption, width=15)

    # Calculate the size of the text box based on the wrapped text for the second box
    text_box_width2, text_box_height2 = calculate_multiline_textbbox(draw, flashy_font2, wrapped_text2,
                                                                     image_width * 0.8)

    # Create a rectangle as a background for the text for the second box
    rect_width2 = text_box_width2 + 40
    rect_height2 = text_box_height2 + 50

    # Border color
    border_color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Border thickness
    border_thickness2 = 5

    # Draw the background for the second box with the chosen color
    draw.rectangle(
        [rect_left2, rect_top2, rect_left2 + rect_width2, rect_top2 + rect_height2],
        fill=background_color2
    )

    # Draw the border for the second box
    draw.rectangle(
        [rect_left2 - border_thickness2, rect_top2 - border_thickness2,
         rect_left2 + rect_width2 + border_thickness2, rect_top2 + rect_height2 + border_thickness2],
        outline=border_color2, width=border_thickness2
    )

    # Calculate the text position to center it in the second box
    text_position2 = (
        rect_left2 + (rect_width2 - text_box_width2) / 2.5,
        rect_top2 + (rect_height2 - text_box_height2) / 3
    )

    # Add the wrapped text to the image for the second box
    for line in textwrap.wrap(wrapped_text2, width=20):
        bbox2 = draw.textbbox(text_position2, line, font=flashy_font2)
        draw.text(text_position2, line, font=flashy_font2, fill=text_color2)
        text_position2 = (text_position2[0], bbox2[3])

    # Save the modified image
    output_image_path = os.path.join('static', 'output_image.jpg')
    image.save(output_image_path)
    print(f"Captions added, borders and backgrounds drawn, and image saved to {output_image_path}")

    return output_image_path

# Specify the upload folder and allowed extensions
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return {"message": "No file part", "result": "error"}

    file = request.files['file']

    # If the user does not select a file, the browser also
    # submits an empty part without a filename
    if file.filename == '':
        return {"message": "No selected file", "result": "error"}

    if file and allowed_file(file.filename):
        # Save the uploaded file to the upload folder
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Perform image processing with the provided caption
        user_caption = request.form.get('caption', '')  # Get the user-provided caption from the form
        processed_image_path = add_caption_to_image(file_path, 'output_image.jpg', user_caption)

        # Render the template with the processed image and file paths
        return render_template('result.html', processed_image='/static/output_image.jpg', download_link='/static/output_image.jpg', original_file_path=file_path)

    return {"message": "Invalid file type", "result": "error"}

# ... (remaining code)

@app.route('/download')
def download():
    # Provide the path to the processed image for download
    processed_image_path = os.path.join('static', 'output_image.jpg')
    return send_file(processed_image_path, as_attachment=True)

@app.route('/reprocess_image', methods=['POST'])
def reprocess_image():
    # Retrieve the original file path and caption from the previous request
    original_file_path = request.form['original_file_path']
    caption = request.form['caption']

    # Perform the image processing with the provided caption
    processed_image_path = add_caption_to_image(original_file_path, 'output_image.jpg', caption)

    # Return the updated processed image for display
    return render_template('result.html', processed_image=processed_image_path, download_link='/static/output_image.jpg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

