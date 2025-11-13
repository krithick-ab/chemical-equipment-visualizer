import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/');
  };

  const showLogoutButton = location.pathname !== '/' && localStorage.getItem('access_token');

  return (
    <header className="bg-blue-600 shadow-md w-full">
      <div className="container mx-auto p-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white font-serif">Chem CSV Visualizer</h1>
        {showLogoutButton && (
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
          >
            Logout
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;