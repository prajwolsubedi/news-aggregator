import React from "react";

const CubeFace: React.FC<{ className: string }> = ({ className }) => (
  <div className={`cube-face ${className}`}>
    {[...Array(9)].map((_, i) => (
      <div key={i} className="cube-cell"></div>
    ))}
  </div>
);

const RubiksCube: React.FC = () => {
  return (
    <div className="cube-container flex items-center justify-center p-20">
      <div className="cube">
        <CubeFace className="cube-face-front" />
        <CubeFace className="cube-face-back" />
        <CubeFace className="cube-face-left" />
        <CubeFace className="cube-face-right" />
        <CubeFace className="cube-face-top" />
        <CubeFace className="cube-face-bottom" />
      </div>
    </div>
  );
};

export default RubiksCube;
