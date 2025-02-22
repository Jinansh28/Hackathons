import React, { useState } from 'react';
import API from '../services/api';

const StudentForm = () => {
  const [name, setName] = useState('');
  const [rollNumber, setRollNumber] = useState('');
  const [faceEncoding, setFaceEncoding] = useState(''); // Placeholder for now
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await API.post('/students/', {
        name,
        roll_number: rollNumber,
        face_encoding: faceEncoding,
      });

      setMessage(response.data.message);
      setName('');
      setRollNumber('');
      setFaceEncoding('');
    } catch (error) {
      setMessage('Error adding student: ' + error.response?.data?.error || error.message);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Add Student</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700">Name</label>
          <input
            type="text"
            className="w-full p-2 border rounded"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700">Roll Number</label>
          <input
            type="text"
            className="w-full p-2 border rounded"
            value={rollNumber}
            onChange={(e) => setRollNumber(e.target.value)}
            required
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700">Face Encoding (JSON String)</label>
          <input
            type="text"
            className="w-full p-2 border rounded"
            value={faceEncoding}
            onChange={(e) => setFaceEncoding(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          Add Student
        </button>
      </form>

      {message && <p className="mt-4 text-center">{message}</p>}
    </div>
  );
};

export default StudentForm;
