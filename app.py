from flask import Flask, render_template

app = Flask(__name__)

# Main Route pointing to your index.html
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/grade-evaluator')
def grade_evaluator():
    return render_template('grade_evaluator.html')

@app.route('/scholarship')
def scholarship():
    return render_template('scholarship.html')

@app.route('/promissory')
def promissory():
    return render_template('promissory.html')

@app.route('/records')
def records():
    return render_template('records.html')

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/leave')
def leave():
    return render_template('leave.html')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

SAVED_RECORDS = []

DOCUMENT_CHECKLIST = [
    "Report Card (Form 138)",
    "School ID Copy (2 copies)",
    "Certificate of Enrollment",
    "Certificate of Good Moral Character",
    "Form 137 (Transcript)",
    "PSA Birth Certificate"
]

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html', records_count=len(SAVED_RECORDS))

@app.route('/grade-evaluator', methods=['GET', 'POST'])
def grade_evaluator():
    evaluation = None
    if request.method == 'POST':
        try:
            student_name = request.form.get('student_name', 'Student').strip()
            student_id = request.form.get('student_id', 'N/A').strip()
            subject_names = request.form.getlist('subject_name')
            units = request.form.getlist('units')
            grades = request.form.getlist('grade')

            total_units = 0.0
            weighted_sum = 0.0
            sum_grades = 0.0
            subjects_list = []

            for sub, u, g in zip(subject_names, units, grades):
                u_val = float(u) if u else 0.0
                g_val = float(g) if g else 0.0
                if u_val > 0:
                    total_units += u_val
                    weighted_sum += (u_val * g_val)
                    sum_grades += g_val
                    subjects_list.append({"name": sub if sub else "Subject", "grade": g_val})

            total_subjects = len(subjects_list)
            gwa = (weighted_sum / total_units) if total_units > 0 else 0.0
            simple_avg = (sum_grades / total_subjects) if total_subjects > 0 else 0.0

            if subjects_list:
                highest = max(subjects_list, key=lambda x: x['grade'])
                lowest = min(subjects_list, key=lambda x: x['grade'])
                highest_str = f"{highest['grade']:.2f}% ({highest['name']})"
                lowest_str = f"{lowest['grade']:.2f}% ({lowest['name']})"
            else:
                highest_str = "--"
                lowest_str = "--"

            # Honor Standing Title
            if gwa >= 95:
                status = "Highest Honor"
            elif gwa >= 90:
                status = "High Honor"
            elif gwa >= 85:
                status = "Honor"
            else:
                status = "No Honor"

            # Equivalent Scale GPA
            if gwa >= 97: gpa_scale = "1.00"
            elif gwa >= 94: gpa_scale = "1.25"
            elif gwa >= 91: gpa_scale = "1.50"
            elif gwa >= 88: gpa_scale = "1.75"
            elif gwa >= 85: gpa_scale = "2.00"
            elif gwa >= 82: gpa_scale = "2.25"
            elif gwa >= 79: gpa_scale = "2.50"
            elif gwa >= 76: gpa_scale = "2.75"
            elif gwa >= 75: gpa_scale = "3.00"
            else: gpa_scale = "5.00 (Failed)"

            # Parity check
            round_gwa = round(gwa)
            round_avg = round(simple_avg)
            gwa_parity = "Even" if round_gwa % 2 == 0 else "Odd"
            avg_parity = "Even" if round_avg % 2 == 0 else "Odd"
            parity_str = f"GWA is {gwa_parity} ({round_gwa}), Avg is {avg_parity} ({round_avg})"

            evaluation = {
                "date_recorded": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "type": "Grade & GPA Evaluation",
                "name": student_name if student_name else "Student",
                "student_id": student_id if student_id else "N/A",
                "total_subjects": total_subjects,
                "total_units": total_units,
                "simple_avg": round(simple_avg, 2),
                "gwa": round(gwa, 2),
                "gpa_scale": gpa_scale,
                "status": status,
                "highest": highest_str,
                "lowest": lowest_str,
                "parity": parity_str,
                "total_grant": 0.00,
                "remark": f"GWA: {round(gwa, 2)}% | Units: {total_units}"
            }

            SAVED_RECORDS.append(evaluation)
        except Exception as e:
            print("Error evaluating grades:", e)

    return render_template('grade_evaluator.html', evaluation=evaluation)

@app.route('/scholarship', methods=['GET', 'POST'])
def scholarship():
    result = None
    error = None

    if request.method == 'POST':
        apply_choice = request.form.get('apply_choice', 'No')

        if apply_choice == 'Yes':
            name = request.form.get('name', '').strip()
            student_id = request.form.get('student_id', '').strip()
            school = request.form.get('school', 'Araullo University').strip()
            year = request.form.get('year', '')
            
            try:
                grade_req = float(request.form.get('grade_maintenance', 85.0))
                current_grade = float(request.form.get('current_grade', 0.0))
                days_left = int(request.form.get('days_left', 0))
            except ValueError:
                error = "Please enter valid numeric values for grades and days left."
                return render_template('scholarship.html', docs=DOCUMENT_CHECKLIST, error=error)

            submitted_docs = request.form.getlist('submitted_docs')
            doc_count = len(submitted_docs)
            total_docs = len(DOCUMENT_CHECKLIST)

            is_grade_met = current_grade >= grade_req
            is_docs_complete = doc_count == total_docs

            if is_grade_met and is_docs_complete:
                status = "Qualified / Approved"
                total_grant = 15000.00
                remark = "All requirements satisfied. Full scholarship discount applied."
            elif is_grade_met and not is_docs_complete:
                status = "Conditional Pending Documents"
                total_grant = 7500.00
                remark = f"Grade requirement met. Please submit remaining {total_docs - doc_count} document(s) within {days_left} day(s)."
            else:
                status = "Disqualified"
                total_grant = 0.00
                remark = "General average does not meet minimum required scholarship maintenance percentage."

            result = {
                "date_recorded": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "type": "Scholarship Evaluation",
                "name": name,
                "student_id": student_id,
                "school": school,
                "year": year,
                "current_grade": current_grade,
                "status": status,
                "total_grant": total_grant,
                "docs_count": doc_count,
                "total_docs": total_docs,
                "days_left": days_left,
                "remark": remark
            }

            SAVED_RECORDS.append(result)

    return render_template('scholarship.html', docs=DOCUMENT_CHECKLIST, result=result, error=error)

@app.route('/promissory', methods=['GET', 'POST'])
def promissory():
    note_submitted = False
    if request.method == 'POST':
        note_submitted = True
    return render_template('promissory.html', note_submitted=note_submitted)

@app.route('/records')
def records():
    return render_template('records.html', records=SAVED_RECORDS)

@app.route('/clear-records')
def clear_records():
    SAVED_RECORDS.clear()
    return redirect(url_for('records'))

@app.route('/export-records')
def export_records():
    if not SAVED_RECORDS:
        return "No evaluation records available to export.", 400

    lines = [
        "==================================================",
        " ARAULLO UNIVERSITY - STUDENT ACADEMIC RECORDS",
        "==================================================\n"
    ]
    
    for idx, rec in enumerate(SAVED_RECORDS, 1):
        lines.append(f"[{idx}] {rec.get('type', 'Record')}")
        lines.append(f"Date & Time: {rec.get('date_recorded', 'N/A')}")
        lines.append(f"Student Name: {rec.get('name', 'N/A')}")
        lines.append(f"Student ID: {rec.get('student_id', 'N/A')}")
        lines.append(f"Status: {rec.get('status', 'N/A')}")
        lines.append(f"Grant / GWA Info: {rec.get('remark', 'N/A')}")
        lines.append("-" * 50 + "\n")

    txt_data = "\n".join(lines)
    return Response(
        txt_data,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=araullo_academic_records.txt"}
    )

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/leave')
def leave():
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
