import React from 'react';
import "../styles/modals.css";


interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode; 
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;  
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {children} 
      </div>
    </div>
  );
};

export default Modal;
