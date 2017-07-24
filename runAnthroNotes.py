from flask import Flask, render_template, request
import scripts.exportToGlobalAnthroNotes
# create an object that is an instance of the flask framework
app = Flask(__name__)

# app routing: to trigger the function backend languages....???
# when the user goes to the url / it will run the index function
@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        age = request.form['agefrm']
        scripts.exportToGlobalAnthroNotes.export_csv_to_global_anthro_notes(language='English')
        print "print a printy print"
        print        "print a printy print"
        print "print something to the console"
        print        "print a printy print"
        print        "print a printy print"

        return render_template('age_t3.html', ageRender=age)

    return render_template('shaan3.html')

# we want to run the app
if __name__ == "__main__":
    app.run(debug=True)