import React from 'react';
import { IoMdClose } from "react-icons/io";
import { FaArrowLeft } from "react-icons/fa";
import "../styles/modals.css";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode; 
}

const Dialog: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;  

  return (
    <div className="dialog-overlay">
      <div className="dialog-content">
        <button className="close-btn" onClick={onClose}><IoMdClose/></button>
        {children} 
      </div>
    </div>
  );
};

const SmallDialog: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;  
  return (
    <div className="sm-dialog-overlay">
      <div className="sm-dialog-content">
        {children} 
      </div>
    </div>
  );
};

export {Dialog, SmallDialog};