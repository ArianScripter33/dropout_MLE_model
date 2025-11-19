import React, { useState, useRef } from 'react';
import Papa from 'papaparse';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';
import { Upload, Trophy, Sparkles, Star } from 'lucide-react';

interface Participant {
    email: string;
    [key: string]: any;
}

interface Winner {
    email: string;
    prize: string;
}

export const Raffle = () => {
    const [participants, setParticipants] = useState<Participant[]>([]);
    const [winners, setWinners] = useState<Winner[]>([]);
    const [isSpinning, setIsSpinning] = useState(false);
    const [prizeConfig, setPrizeConfig] = useState<'one' | 'two'>('one');
    const [currentCandidate, setCurrentCandidate] = useState<string>("");
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                const data = results.data as Participant[];
                const validParticipants = data.filter(p => p.email && p.email.includes('@'));

                if (validParticipants.length === 0) {
                    const headers = results.meta.fields || Object.keys(data[0] || {});
                    alert(`No se encontraron participantes válidos.\n\nColumnas encontradas: ${headers.join(', ')}\n\nEsperaba: 'email'.`);
                } else {
                    setParticipants(validParticipants);
                }
            },
            error: () => {
                alert("Error al leer el archivo CSV.");
            }
        });
    };

    const spinRaffle = async () => {
        if (participants.length === 0) return;
        setIsSpinning(true);
        setWinners([]);

        const shuffled = [...participants].sort(() => 0.5 - Math.random());
        let selectedWinners: Winner[] = [];

        if (prizeConfig === 'one') {
            selectedWinners = [{ email: shuffled[0].email, prize: '$300 MXN Uber/Eats' }];
        } else {
            selectedWinners = [
                { email: shuffled[0].email, prize: '$150 MXN Uber/Eats' },
                { email: shuffled[1].email, prize: '$150 MXN Uber/Eats' }
            ];
        }

        const duration = 10000; // 10 seconds for more suspense
        const startTime = Date.now();

        const animateTicker = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;

            if (progress < 1) {
                // Ease out cubic
                const interval = Math.max(50, 500 * Math.pow(progress, 3));
                const randomIdx = Math.floor(Math.random() * participants.length);
                setCurrentCandidate(participants[randomIdx].email);
                setTimeout(() => requestAnimationFrame(animateTicker), interval);
            } else {
                setIsSpinning(false);
                setWinners(selectedWinners);
                triggerConfetti();
            }
        };

        animateTicker();
    };

    const triggerConfetti = () => {
        const duration = 5 * 1000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };
        const random = (min: number, max: number) => Math.random() * (max - min) + min;

        const interval = setInterval(() => {
            const timeLeft = animationEnd - Date.now();
            if (timeLeft <= 0) {
                return clearInterval(interval);
            }
            const particleCount = 50 * (timeLeft / duration);
            confetti({ ...defaults, particleCount, origin: { x: random(0.1, 0.3), y: Math.random() - 0.2 } });
            confetti({ ...defaults, particleCount, origin: { x: random(0.7, 0.9), y: Math.random() - 0.2 } });
        }, 250);
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white flex flex-col relative overflow-hidden font-sans selection:bg-gold-500/30">
            {/* Cinematic Background */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-purple-900/10 via-[#050505] to-[#050505] pointer-events-none" />
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-15 mix-blend-overlay pointer-events-none"></div>

            {/* Ticker Tape - Always visible if participants exist */}
            {participants.length > 0 && !winners.length && (
                <div className="absolute top-0 left-0 right-0 h-12 bg-white/5 border-b border-white/5 backdrop-blur-sm flex items-center overflow-hidden z-20">
                    <motion.div
                        className="flex gap-8 whitespace-nowrap text-white/30 text-sm font-mono tracking-wider"
                        animate={{ x: [0, -1000] }}
                        transition={{ repeat: Infinity, duration: 20, ease: "linear" }}
                    >
                        {[...participants, ...participants, ...participants].map((p, i) => (
                            <span key={i} className="flex items-center gap-2">
                                <span className="w-1 h-1 bg-gold-500/50 rounded-full" />
                                {p.email}
                            </span>
                        ))}
                    </motion.div>
                </div>
            )}

            <main className="flex-1 flex flex-col items-center justify-center p-8 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1 }}
                    className="max-w-6xl w-full flex flex-col items-center"
                >
                    {/* Header */}
                    <header className="text-center mb-20 space-y-6">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="flex items-center justify-center gap-3 text-gold-400/80 text-sm tracking-[0.3em] uppercase font-medium"
                        >
                            <span className="w-8 h-[1px] bg-gold-400/50" />
                            <Sparkles className="w-4 h-4" />
                            <span>Official Selection</span>
                            <span className="w-8 h-[1px] bg-gold-400/50" />
                        </motion.div>

                        <h1 className="text-7xl md:text-9xl font-serif italic font-medium text-white tracking-tight leading-none">
                            Pulso <br />
                            <span className="not-italic bg-gradient-to-r from-white via-white to-white/50 bg-clip-text text-transparent">Estudiantil</span>
                        </h1>
                    </header>

                    {/* Content Stage */}
                    <div className="w-full max-w-4xl min-h-[400px] flex flex-col items-center justify-center">
                        <AnimatePresence mode="wait">
                            {participants.length === 0 ? (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    onClick={() => fileInputRef.current?.click()}
                                    className="group cursor-pointer flex flex-col items-center gap-6"
                                >
                                    <div className="w-20 h-20 rounded-full border border-white/10 flex items-center justify-center group-hover:border-gold-500/50 group-hover:scale-110 transition-all duration-500">
                                        <Upload className="w-6 h-6 text-white/40 group-hover:text-gold-400" />
                                    </div>
                                    <div className="text-center space-y-2">
                                        <p className="text-lg font-serif italic text-white/80">Upload Participant Data</p>
                                        <p className="text-xs text-white/30 uppercase tracking-widest">CSV Format Only</p>
                                    </div>
                                    <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept=".csv" className="hidden" />
                                </motion.div>
                            ) : isSpinning ? (
                                <motion.div
                                    key="spinning"
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 1.1 }}
                                    className="text-center w-full"
                                >
                                    <div className="text-xs text-gold-500 uppercase tracking-[0.5em] mb-8 animate-pulse">Selecting Winner</div>
                                    <div className="relative overflow-hidden h-32 flex items-center justify-center">
                                        <div className="absolute inset-0 bg-gradient-to-b from-[#050505] via-transparent to-[#050505] z-10" />
                                        <motion.div
                                            key={currentCandidate}
                                            className="text-5xl md:text-7xl font-serif text-white"
                                        >
                                            {currentCandidate.split('@')[0]}
                                        </motion.div>
                                    </div>
                                </motion.div>
                            ) : winners.length > 0 ? (
                                <div className="w-full grid grid-cols-1 gap-8">
                                    {winners.map((w, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, y: 100, rotateX: -20 }}
                                            animate={{ opacity: 1, y: 0, rotateX: 0 }}
                                            transition={{ type: "spring", bounce: 0.3, duration: 1.5, delay: i * 0.2 }}
                                            className="relative group perspective-1000"
                                        >
                                            {/* Golden Ticket Card */}
                                            <div className="relative bg-gradient-to-br from-[#1a1a1a] to-[#0a0a0a] border border-gold-500/30 p-10 rounded-xl overflow-hidden shadow-[0_0_50px_-10px_rgba(234,179,8,0.15)] group-hover:shadow-[0_0_80px_-20px_rgba(234,179,8,0.3)] transition-shadow duration-700">
                                                {/* Shine Effect */}
                                                <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

                                                <div className="flex items-start justify-between relative z-10">
                                                    <div>
                                                        <div className="flex items-center gap-3 mb-4">
                                                            <Star className="w-4 h-4 text-gold-500 fill-gold-500" />
                                                            <span className="text-gold-500 text-xs font-bold tracking-[0.2em] uppercase">Winner No. {i + 1}</span>
                                                        </div>
                                                        <h3 className="text-4xl md:text-5xl font-serif text-white mb-2">{w.email}</h3>
                                                        <p className="text-white/40 font-mono text-sm">{w.prize}</p>
                                                    </div>
                                                    <Trophy className="w-16 h-16 text-gold-500/20" />
                                                </div>

                                                {/* Decorative Bottom Bar */}
                                                <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-gold-500/50 to-transparent" />
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-12 w-full">
                                    {/* Controls */}
                                    <div className="flex gap-8">
                                        <button
                                            onClick={() => setPrizeConfig('one')}
                                            className={`text-sm tracking-widest uppercase transition-all duration-300 ${prizeConfig === 'one' ? 'text-gold-400 border-b border-gold-400' : 'text-white/30 hover:text-white'}`}
                                        >
                                            1 Winner
                                        </button>
                                        <button
                                            onClick={() => setPrizeConfig('two')}
                                            className={`text-sm tracking-widest uppercase transition-all duration-300 ${prizeConfig === 'two' ? 'text-gold-400 border-b border-gold-400' : 'text-white/30 hover:text-white'}`}
                                        >
                                            2 Winners
                                        </button>
                                    </div>

                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={spinRaffle}
                                        className="group relative px-16 py-6 bg-white text-black rounded-sm font-serif italic text-2xl overflow-hidden"
                                    >
                                        <div className="absolute inset-0 bg-gold-400 opacity-0 group-hover:opacity-100 transition-opacity duration-500 mix-blend-multiply" />
                                        <span className="relative z-10 flex items-center gap-4">
                                            Reveal Winner
                                        </span>
                                    </motion.button>

                                    <div className="text-white/20 font-mono text-xs">
                                        {participants.length} ENTRIES VERIFIED
                                    </div>
                                </div>
                            )}
                        </AnimatePresence>
                    </div>
                </motion.div>
            </main>
        </div>
    );
};
