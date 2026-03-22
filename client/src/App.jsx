import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar'; // Make sure to import the Navbar
import { Home } from './pages/Home';
import Register from './pages/Register';
import Login from './pages/Login';
import TransactionPage  from './pages/TransactionPage';

const App = () => {
  return (
    <BrowserRouter>
      <Navbar />
      <div style={{ marginTop: '80px' }}> 
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} /> 
          <Route path="/transactions" element={<TransactionPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};
export default App;
