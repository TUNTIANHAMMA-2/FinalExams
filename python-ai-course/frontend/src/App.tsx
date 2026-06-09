import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import LiveAttendance from './pages/LiveAttendance';
import Register from './pages/Register';
import Records from './pages/Records';
import Stats from './pages/Stats';
import StudentAnalysis from './pages/StudentAnalysis';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/live" replace />} />
          <Route path="live" element={<LiveAttendance />} />
          <Route path="register" element={<Register />} />
          <Route path="records" element={<Records />} />
          <Route path="stats" element={<Stats />} />
          <Route path="analysis" element={<StudentAnalysis />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
