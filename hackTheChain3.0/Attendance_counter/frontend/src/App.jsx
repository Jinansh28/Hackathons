import React from 'react';
import StudentForm from './components/StudentForm';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-4xl font-bold text-center mb-8">Attendance Monitoring System</h1>
      <StudentForm />
      <Dashboard />
    </div>
  );
}

export default App;
