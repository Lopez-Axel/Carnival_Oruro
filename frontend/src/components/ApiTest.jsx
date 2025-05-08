import React, { useState, useEffect } from 'react';

const ApiTest = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/data')
      .then(res => {
        if (!res.ok) throw new Error(`Error ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch(setError);
  }, []);

  if (error) return <p style={{ color: 'red' }}>Error: {error.message}</p>;
  if (!data) return <p>Loading...</p>;
  
  return <p>Mensaje: <strong>{data.message} , {data.data}</strong></p>;
};

export default ApiTest;
