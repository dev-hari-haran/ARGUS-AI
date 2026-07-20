import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Test from './pages/Test';
import ScrollButtons from './components/ScrollButtons';
import './index.css';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="app-container">
          <Sidebar />
          <main className="page-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/test" element={<Test />} />
            </Routes>
          </main>
          <ScrollButtons />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
