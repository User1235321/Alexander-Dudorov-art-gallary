import React from 'react';
import styles from './Footer.module.css';

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.content}>
        <p className={styles.logo}>Галерея Александра Дудорова</p>
        <div className={styles.columns}>
          <div className={styles.column}>
            <p>© 2025 Санкт-Петербургский политехнический университет</p>
            <p className={styles.copyright}>При использовании материалов активная ссылка обязательна</p>
          </div>
          <div className={styles.column}>
            <p>Политика конфиденциальности</p>
            <p>Положение об использовании «cookie» файлов</p>
          </div>
          <div className={styles.column}>
            <p>Контакты</p>
            <p>пр-т. Энгельса, 23, Санкт-Петербург, 194156</p>
            <p>+7 (999) 999 99 99</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;