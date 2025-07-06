import React, { useState, useEffect } from 'react';

const NotificationContainer = () => {
  const [notifications, setNotifications] = useState([]);

  // Function to add notification (can be called from anywhere in the app)
  const addNotification = (type, message, duration = 5000) => {
    const id = Date.now();
    const notification = { id, type, message };
    
    setNotifications(prev => [...prev, notification]);
    
    setTimeout(() => {
      removeNotification(id);
    }, duration);
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  // Make addNotification available globally
  useEffect(() => {
    window.showNotification = addNotification;
    return () => {
      delete window.showNotification;
    };
  }, []);

  return (
    <div 
      className="position-fixed top-0 end-0 p-3" 
      style={{ zIndex: 9999 }}
    >
      {notifications.map(notification => (
        <div
          key={notification.id}
          className={`alert alert-${notification.type === 'error' ? 'danger' : notification.type} alert-dismissible fade show mb-2`}
          role="alert"
        >
          <i className={`fas ${
            notification.type === 'success' ? 'fa-check-circle' :
            notification.type === 'error' ? 'fa-exclamation-triangle' :
            notification.type === 'warning' ? 'fa-exclamation-triangle' :
            'fa-info-circle'
          } me-2`}></i>
          {notification.message}
          <button
            type="button"
            className="btn-close"
            onClick={() => removeNotification(notification.id)}
          ></button>
        </div>
      ))}
    </div>
  );
};

export default NotificationContainer;