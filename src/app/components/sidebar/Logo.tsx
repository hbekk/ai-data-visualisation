import React from "react";
import Image from 'next/image';
import '../../styles/Sidebar/logo.css'; 
import AssetPicker from './assetPicker';

export default function Logo() {
  
  return (
    <div className="logo-container">
      <Image
        className="logo"
        alt="Twilligent logo"
        src="/logo.png" 
        width={300}
        height={300}
        loading="lazy"
      />
      <AssetPicker />
    </div>
  );
}
