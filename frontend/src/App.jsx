import './App.css';
import './index.css'
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Admin from "./components/Admin";
import MainPage from "./components/MainPage";


function App() {
  return (
      <div>
        <Router>
          <Routes>
            <Route path="/" element={<MainPage/>}/>
            <Route path="/admin" element={<Admin/>}/>
          </Routes>
        </Router>
      </div>
  );
}


export default App;