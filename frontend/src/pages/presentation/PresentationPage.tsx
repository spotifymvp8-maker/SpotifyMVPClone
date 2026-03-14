import React from "react";
import { motion } from "framer-motion";
import { SiVite, SiReact, SiTypescript, SiTailwindcss, SiPostgresql, SiDocker, SiFastapi } from "react-icons/si";

const icons = [
  { Icon: SiVite, label: "Vite", color: "#646CFF" },
  { Icon: SiReact, label: "React", color: "#61DAFB" },
  { Icon: SiTypescript, label: "TypeScript", color: "#3178C6" },
  { Icon: SiTailwindcss, label: "Tailwind", color: "#38BDF8" },
  { Icon: SiPostgresql, label: "PostgreSQL", color: "#336791" },
  { Icon: SiDocker, label: "Docker", color: "#2496ED" },
  { Icon: SiFastapi, label: "FastAPI", color: "#009688" },
];

export default function ProjectPresentation() {
  return (
    <div className="relative flex items-center justify-center min-h-screen bg-neutral-950 overflow-hidden">
      <OrbitalIcons />
      <CenterLogo />
      <BackgroundGlow />
    </div>
  );
}

function CenterLogo() {
  return (
    <div className="relative z-10 flex flex-col items-center justify-center">

      <motion.div
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 3, repeat: Infinity }}
        className="w-40 h-40 md:w-56 md:h-56 rounded-3xl bg-neutral-900 flex items-center justify-center shadow-2xl border border-neutral-800"
      >
        <img
          src="/spotify.png"
          alt="Spotify Clone Logo"
          className="w-16 h-16 md:w-20 md:h-20"
        />
      </motion.div>

        <div className="absolute flex flex-col items-center justify-center pointer-events-none top-full -mt-16 w-full">
          <span className="text-xl md:text-2xl font-bold tracking-wider bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            SPOTIFY CLONE
          </span>
        </div>
    </div>
  );
}

function OrbitalIcons() {
  const radius = 320;

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        className="absolute inset-0 m-auto"
        style={{
          width: radius * 2,
          height: radius * 2,
          transformOrigin: "center",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {icons.map((item, i) => {
          const angle = (i / icons.length) * Math.PI * 2;
          const Icon = item.Icon;

          return (
            <motion.div
              key={i}
              className="absolute"
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: 1,
                scale: 1,
                x: Math.cos(angle) * radius,
                y: Math.sin(angle) * radius,
              }}
              transition={{ delay: i * 0.4, duration: 0.8, ease: "easeOut" }}
              style={{ transform: "translate(-50%, -50%)", position: "absolute" }}
            >
              <div className="p-4 rounded-2xl bg-neutral-900 border border-neutral-800 shadow-xl backdrop-blur relative z-20">
                <Icon className="w-8 h-8 md:w-10 md:h-10" style={{ color: item.color }} />
              </div>
            </motion.div>
          );
        })}
      </motion.div>
    </div>
  );
}

function BackgroundGlow() {
  return (
    <div className="absolute inset-0 -z-10 flex items-center justify-center">
      <div className="w-[600px] h-[600px] bg-cyan-500/10 blur-3xl rounded-full" />
    </div>
  );
}