import openai
from flask import Flask, request, render_template
import docx2txt

openai.api_key = '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'

app = Flask(__name__, static_folder='static')

@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/demo")
def demo():
    return render_template("demo.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    global resume
    file = request.files['resume']
    try:
        file.save('uploads/' + file.filename)
        file_path = file.filename
        try:
            print(f'the name of the uploaded file is: {file.filename}')
            with open("uploads/" + file_path, "r") as file:
                resume = file.read()
                api_response = get_api_response(resume)
                processed_response = process_response(api_response)
        except:
            resume = docx2txt.process("uploads/" + file_path)
            api_response = get_api_response(resume)
            processed_response = process_response(api_response)
        with open("resumefeedback.txt", "w") as output:
            output.write(api_response)
            output.close()
        return render_template("result.html", strengths=processed_response[0], weaknesses=processed_response[1], score=processed_response[2])
    except:
        return render_template("error.html")

def process_response(api_response):
    pos1 = api_response.find('Strengths:')
    pos2 = api_response.find('Weaknesses:')
    pos3 = api_response.find('Score: ')
    print(pos1)
    print(pos2)
    print(pos3)

    strengths = api_response[pos1 + 11: pos2]
    list_of_strengths = strengths.split("- ")
    list_of_strengths.pop(0)
    for i in list_of_strengths:
        print(i)
    print("\n")
    weaknesses = api_response[pos2 + 12: pos3]
    list_of_weaknesses = weaknesses.split("- ")
    list_of_weaknesses.pop(0)
    for i in list_of_weaknesses:
        print(i)

    print("\n")
    score = api_response[pos3 + 7: pos3 + 10]
    if score[2] == "/":
        score = score[0:2] + "%"
    else:
        score = score + "%"
    print(score)

    return [list_of_strengths, list_of_weaknesses, score]



def get_api_response(resume):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional resume reviewer. Provide feedback on the resume, including what the user did well and what they could improve on. Be as detailed and specific as possible and write in point form. You may comment on grammer/spelling, formatting, and content. At the end of your feedback, assign a percentage score (out of 100) based on the quality of the resume. You should follow this format: Strengths: [what the user did well] Weaknesses: [what the user could improve on] Score: [a score out of 100]."},
            {"role": "user", "content": f'Can you take a look at my resume? Here\'s my resume: {resume}'}
        ]
    )
    parse_response = response['choices'][0]['message']['content']
    return parse_response



if __name__ == '__main__':
    app.run(debug=True, port=5000)



