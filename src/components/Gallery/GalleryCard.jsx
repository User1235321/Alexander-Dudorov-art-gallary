import React from 'react';
import styles from './Gallery.module.css';

const GalleryCard = ({ image, title, year, description }) => {
  return (
    <div className={styles.card}>
      <img src={image} alt={title} className={styles.image} />
      <div className={styles.content}>
        <div className={styles.title}>
          <h3>{title}</h3>
          <p>{year}</p>
        </div>
        <p>{description}</p>
      </div>
    </div>
  );
};

export default GalleryCard;