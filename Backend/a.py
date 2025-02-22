@app.route('/get_attendance', methods=['POST'])
def get_attendance():
    data = request.get_json()
    teacher_name = data.get('teacher_name')

    # Sanitize teacher name for file naming
    safe_teacher_name = teacher_name.replace(" ", "_").lower()
    teacher_file = f"{safe_teacher_name}.csv"

    if os.path.exists(teacher_file):
        df = pd.read_csv(teacher_file)

        if df.empty:
            return jsonify({"records": [], "summary": []})

        # Convert attendance records to a list of dictionaries
        records = df.to_dict(orient="records")

        # Generate summary (total classes attended per student)
        summary = df[df["Status"] == "Present"].groupby("Student ID").size().reset_index(name="Total Classes Attended")
        summary_list = summary.to_dict(orient="records")

        return jsonify({"records": records, "summary": summary_list})
    else:
        return jsonify({"records": [], "summary": []})