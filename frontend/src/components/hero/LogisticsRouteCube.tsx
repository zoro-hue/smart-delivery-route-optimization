import React, { useRef } from 'react';
import { useTheme } from '../../context/ThemeContext';

/**
 * LogisticsRouteCube
 *
 * Renders the high-definition animated 3D logistics route cube video
 * showing the 3x3x3 isometric grid with four colored logistics routes
 * and mini delivery vehicles moving across the cube surfaces.
 */
export const LogisticsRouteCube: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div className="relative w-full h-full flex items-center justify-center select-none overflow-hidden">
      {/* High-Definition 3D Logistics Route Cube Animation with theme adaptation */}
      <div className="w-full h-full min-h-[380px] sm:min-h-[460px] lg:min-h-[520px] flex items-center justify-center p-2 sm:p-4">
        <div
          className={`relative rounded-3xl overflow-hidden p-1.5 transition-all duration-300 ${
            isDark
              ? 'bg-[#18181E]/80 border border-white/10 shadow-[0_20px_60px_-10px_rgba(0,0,0,0.7)] backdrop-blur-md'
              : ''
          }`}
        >
          <video
            ref={videoRef}
            src="/cube.mp4"
            autoPlay
            loop
            muted
            playsInline
            className={`w-full h-full max-h-[460px] sm:max-h-[500px] lg:max-h-[540px] object-contain rounded-2xl drop-shadow-[0_12px_24px_rgba(0,0,0,0.12)] ${
              isDark ? 'contrast-[1.05] brightness-[0.95]' : ''
            }`}
            title="ROUTE/IQ 3D Logistics Route Cube Animation"
          />
        </div>
      </div>
    </div>
  );
};
