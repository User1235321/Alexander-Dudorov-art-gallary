import React from 'react';
import GalleryCard from './GalleryCard';
import styles from './Gallery.module.css';

const Gallery = () => {
  const paintings = [
    {
      image: '/images/image-99.png',
      title: 'Маки у пруда',
      year: '2022 г.',
      description: 'Холст,масло. Частная коллекция.'
    },
    // Добавьте остальные картины из index.html
  ];

  return (
    <div className={styles.gallery}>
      <h2>КАРТИНЫ</h2>
      <div className={styles.grid}>
        {paintings.map((painting, index) => (
          <GalleryCard key={index} {...painting} />
        ))}
      </div>
    </div>
  );
};

export default Gallery;