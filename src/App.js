import React from 'react';
import Header from './components/Header/Header';
import Gallery from './components/Gallery/Gallery';
import ContactForm from './components/ContactForm/ContactForm';
import Footer from './components/Footer/Footer';
import './styles/global.css';

const App = () => {
  return (
    <div className="app">
      <Header />
      <main>
        <Gallery />
        <ContactForm />
      </main>
      <Footer />
    </div>
  );
};

export default App;