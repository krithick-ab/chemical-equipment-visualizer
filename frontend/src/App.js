import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/common/Header';
import HomePage from './components/pages/HomePage';
import ResultsPage from './components/pages/ResultsPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/results/:id" element={<ResultsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;