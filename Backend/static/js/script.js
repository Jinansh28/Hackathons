function viewAttendance(teacher) {
    window.location.href = `/profile?teacher=${encodeURIComponent(teacher)}`;
}

function fetchAttendance(teacher) {
    fetch('/get_attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ teacher_name: teacher }),
    })
    .then(response => response.json())
    .then(data => {
        const tbody = document.getElementById('attendance-records');
        tbody.innerHTML = '';

        if (data.message === "No records found") {
            tbody.innerHTML = '<tr><td colspan="3">No records found.</td></tr>';
            return;
        }

        data.records.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.Date}</td>
                <td>${record['Student ID']}</td>
                <td>${record.Status}</td>
            `;
            tbody.appendChild(row);
        });
    })
    .catch(error => console.error('Error fetching attendance:', error));
}