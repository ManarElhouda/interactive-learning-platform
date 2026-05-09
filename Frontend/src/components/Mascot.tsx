import mascot from "@/assets/mascot.png";
import { motion } from "framer-motion";

type Mood = "idle" | "thinking" | "celebrate" | "sleep";

export function Mascot({ mood = "idle", size = 140 }: { mood?: Mood; size?: number }) {
  const animate =
    mood === "celebrate"
      ? { y: [0, -20, 0], rotate: [0, -8, 8, 0] }
      : mood === "thinking"
      ? { rotate: [0, 4, -4, 0] }
      : mood === "sleep"
      ? { y: [0, 2, 0] }
      : { y: [0, -6, 0] };

  const transition =
    mood === "celebrate"
      ? { duration: 0.6, repeat: 2 }
      : { duration: mood === "sleep" ? 4 : 3, repeat: Infinity, ease: "easeInOut" as const };

  return (
    <motion.div animate={animate} transition={transition} style={{ width: size, height: size }}>
      <img src={mascot} alt="Beyond 21 mascot" width={size} height={size} className="drop-shadow-xl" />
    </motion.div>
  );
}
