import React, { useEffect, useState } from 'react';
import API from '../services/api';

const Dashboard = () => {
  const [students, setStudents] = useState([]);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const response = await API.get('/students/');
        setStudents(response.data);
      } catch (error) {
        console.error('Error fetching students:', error);
      }
    };

    fetchStudents();
  }, []);

  return (
    <div className="max-w-4xl mx-auto mt-10">
      <h2 className="text-3xl font-bold mb-4">Student List</h2>
      <ul className="bg-white shadow-md rounded-lg p-4">
        {students.map((student) => (
          <li key={student.id} className="border-b p-2">
            {student.name} - {student.roll_number}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;
