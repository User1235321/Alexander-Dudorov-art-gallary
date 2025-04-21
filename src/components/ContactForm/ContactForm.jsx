import React, { useState } from 'react';
import styles from './ContactForm.module.css';

const ContactForm = () => {
  const [formData, setFormData] = useState({ name: '', email: '', comment: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Форма отправлена:', formData);
  };

  return (
    <div className={styles.contactForm}>
      <h2>Свяжитесь с нами:</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ваше ФИО"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
        <input
          type="email"
          placeholder="Ваш Email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        />
        <textarea
          placeholder="Ваш комментарий"
          value={formData.comment}
          onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
        />
        <button type="submit">Отправить</button>
      </form>
    </div>
  );
};

export default ContactForm;