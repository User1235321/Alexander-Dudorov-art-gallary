import React from 'react';
import styles from './Header.module.css';
import vector11 from '../../assets/images/vector-11.svg';

const Header = () => {
  return (
    <header className={styles.header}>
      <p className={styles.textBlack}>КОНТАКТЫ</p>
      <nav className={styles.navbar}>
        <div className={styles.container}>
          <p className={styles.textWhite}>Галерея Александра Дудорова</p>
          <div className={styles.column}>
            <div className={styles.navLinkDropdown}>
              <p className={styles.textWhite}>RU</p>
              <div className={styles.chevronDown}>
                <img src={vector11} alt="Dropdown" />
              </div>
            </div>
            <div className={styles.menu}>
              <p className={styles.textWhite}>Выставки</p>
              <p className={styles.textWhite}>О художнике</p>
              <p className={styles.textWhite}>Картины</p>
              <p className={styles.textWhite}>Контакты</p>
            </div>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;