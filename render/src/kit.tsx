import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {loadFont} from '@remotion/google-fonts/BebasNeue';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';

export const {fontFamily: BIG} = loadFont();
export const {fontFamily: SM} = loadInter('normal', {weights: ['700', '900']});

export const C = {
	bg: '#0B1220',
	panel: '#16213A',
	y: '#FFD400',
	r: '#FF3B3B',
	g: '#5BE33B',
	w: '#F5F7FA',
	grey: '#8A96A8',
	acid: '#C8E64B',
	lead: '#6F7B8C',
	cry: '#EAF2FF',
	water: '#7CC8FF',
};

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const lerp = (f: number, a: number, b: number, from: number, to: number, ease = Easing.out(Easing.cubic)) =>
	interpolate(f, [a, b], [from, to], {...clamp, easing: ease});

export const usePop = (delay: number) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return spring({frame: frame - delay, fps, config: {damping: 11, stiffness: 160}});
};

export const Bg: React.FC<{children: React.ReactNode; tint?: string}> = ({children, tint = '#1B2A4A'}) => {
	const frame = useCurrentFrame();
	return (
		<AbsoluteFill style={{background: `radial-gradient(circle at 50% 40%, ${tint} 0%, ${C.bg} 70%)`, overflow: 'hidden'}}>
			<AbsoluteFill
				style={{
					opacity: 0.12,
					backgroundImage:
						'linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px)',
					backgroundSize: '90px 90px',
					backgroundPosition: `0 ${frame * 0.6}px`,
				}}
			/>
			{children}
		</AbsoluteFill>
	);
};

export const Label: React.FC<{text: string; delay: number; y: number; size?: number; color?: string; sub?: boolean}> = ({
	text,
	delay,
	y,
	size = 110,
	color = C.w,
	sub = false,
}) => {
	const p = usePop(delay);
	return (
		<div
			style={{
				position: 'absolute',
				top: y,
				width: '100%',
				textAlign: 'center',
				fontFamily: sub ? SM : BIG,
				fontWeight: 900,
				fontSize: size,
				letterSpacing: sub ? 1 : 3,
				color,
				transform: `scale(${p}) translateY(${(1 - p) * 40}px)`,
				opacity: Math.min(1, p * 2),
				textShadow: '0 8px 0 rgba(0,0,0,0.45)',
				lineHeight: 1,
			}}
		>
			{text}
		</div>
	);
};

export const Counter: React.FC<{
	keys: [number, number][];
	y: number;
	size?: number;
	color: string;
	unit?: string;
}> = ({keys, y, size = 300, color, unit = ''}) => {
	const frame = useCurrentFrame();
	let v = keys[0][1];
	for (let i = 1; i < keys.length; i++) {
		const [f0, v0] = keys[i - 1];
		const [f1, v1] = keys[i];
		if (frame >= f0) v = lerp(frame, f0 + 4, f1, v0, v1);
	}
	const last = keys[keys.length - 1][0];
	const land = spring({frame: frame - last, fps: 30, config: {damping: 9, stiffness: 220}});
	return (
		<div
			style={{
				position: 'absolute',
				top: y,
				width: '100%',
				textAlign: 'center',
				fontFamily: BIG,
				fontSize: size,
				color,
				transform: `scale(${1 + (frame >= last ? (1 - land) * 0.25 : 0)})`,
				textShadow: `0 0 40px ${color}66, 0 10px 0 rgba(0,0,0,0.5)`,
				lineHeight: 1,
			}}
		>
			{Math.round(v)}
			<span style={{fontSize: size * 0.32, marginLeft: 16, color: C.w}}>{unit}</span>
		</div>
	);
};

// Semicircle gauge. value(frame) supplied by caller so steps can be scripted.
export const Gauge: React.FC<{value: number; max: number; color: string; mark?: number; y: number; label: string}> = ({
	value,
	max,
	color,
	mark,
	y,
	label,
}) => {
	const W = 900;
	const cx = W / 2;
	const cy = 470;
	const R = 400;
	const ang = (v: number) => Math.PI * (1 - Math.min(v, max) / max);
	const pt = (v: number, r: number) => [cx + r * Math.cos(ang(v)), cy - r * Math.sin(ang(v))];
	const arc = (v: number) => {
		const [x, yy] = pt(v, R);
		return `M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${x} ${yy}`;
	};
	const [nx, ny] = pt(value, R - 70);
	return (
		<svg width={W} height={560} style={{position: 'absolute', left: (1080 - W) / 2, top: y}}>
			<path d={arc(max)} stroke="#26324D" strokeWidth={56} fill="none" strokeLinecap="round" />
			<path d={arc(Math.max(value, max * 0.001))} stroke={color} strokeWidth={56} fill="none" strokeLinecap="round" />
			{Array.from({length: 11}).map((_, i) => {
				const v = (max / 10) * i;
				const [x1, y1] = pt(v, R - 44);
				const [x2, y2] = pt(v, R - 74);
				return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={C.grey} strokeWidth={6} />;
			})}
			{mark !== undefined && (() => {
				const [x1, y1] = pt(mark, R + 44);
				const [x2, y2] = pt(mark, R - 44);
				return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={C.y} strokeWidth={10} strokeDasharray="14 10" />;
			})()}
			<line x1={cx} y1={cy} x2={nx} y2={ny} stroke={C.w} strokeWidth={16} strokeLinecap="round" />
			<circle cx={cx} cy={cy} r={34} fill={C.w} />
			<text x={cx} y={cy + 80} textAnchor="middle" fill={C.grey} fontFamily={SM} fontWeight={900} fontSize={40} letterSpacing={4}>
				{label}
			</text>
		</svg>
	);
};

// Cut-away of a lead-acid battery: 6 plates in acid, sulfate crystals grow (grow 0..1) and clear (clear 0..1).
export const Cutaway: React.FC<{grow: number; clear?: number; blocked?: boolean; crack?: boolean; w?: number; x?: number; y: number; plates?: number}> = ({
	grow,
	clear = 0,
	blocked = false,
	crack = false,
	w = 900,
	x,
	y,
	plates = 6,
}) => {
	const frame = useCurrentFrame();
	const H = w * 0.78;
	const pad = w * 0.07;
	const pw = (w - pad * 2) / (plates * 2 - 1);
	const plateX = (i: number) => pad + i * pw * 2;
	const top = H * 0.18;
	const bot = H * 0.94;
	const crystals = Array.from({length: plates * 14}).map((_, i) => {
		const p = i % plates;
		const side = random(`s${i}`) > 0.5 ? 1 : -1;
		const px = plateX(p) + (side > 0 ? pw : 0) + side * random(`o${i}`) * pw * 0.35;
		const py = top + 30 + random(`y${i}`) * (bot - top - 60);
		const t = random(`t${i}`) * 0.85;
		const s = interpolate(grow, [t, t + 0.15], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
		const fade = 1 - interpolate(clear, [random(`c${i}`) * 0.7, random(`c${i}`) * 0.7 + 0.3], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
		const r = (10 + random(`r${i}`) * 16) * (w / 900);
		const pts = Array.from({length: 6}).map((__, k) => {
			const a = (Math.PI / 3) * k + random(`a${i}`);
			return `${px + Math.cos(a) * r * s},${py + Math.sin(a) * r * s}`;
		});
		return <polygon key={i} points={pts.join(' ')} fill={C.cry} opacity={0.92 * fade} stroke="#B9C8E0" strokeWidth={2} />;
	});
	const ions = Array.from({length: 10}).map((_, i) => {
		const lane = top + 40 + (i / 10) * (bot - top - 80);
		const gap = Math.floor(random(`g${i}`) * (plates - 1));
		const x0 = plateX(gap) + pw + 8;
		const x1 = plateX(gap + 1) - 8;
		const span = x1 - x0;
		const ph = ((frame * 4 + random(`p${i}`) * 400) % (span * 2)) / span;
		const tri = ph < 1 ? ph : 2 - ph;
		const reach = blocked ? 0.5 + 0.5 * (1 - grow) : 1;
		const cx = x0 + span * 0.5 + (tri - 0.5) * span * reach;
		return <circle key={i} cx={cx} cy={lane} r={7 * (w / 900)} fill={C.y} opacity={0.9} />;
	});
	return (
		<svg width={w} height={H} style={{position: 'absolute', left: x ?? (1080 - w) / 2, top: y}}>
			<rect x={4} y={top - 20} width={w - 8} height={bot - top + 40} rx={36} fill="#1E2A3F" stroke={C.grey} strokeWidth={8} />
			<rect x={14} y={top + 10} width={w - 28} height={bot - top - 10} rx={24} fill={C.acid} opacity={0.22} />
			<rect x={w * 0.14} y={top - 80} width={w * 0.12} height={64} rx={10} fill={C.r} />
			<rect x={w * 0.74} y={top - 80} width={w * 0.12} height={64} rx={10} fill="#222" stroke={C.grey} strokeWidth={4} />
			<text x={w * 0.2} y={top - 30} textAnchor="middle" fontFamily={BIG} fontSize={56 * (w / 900)} fill={C.w}>+</text>
			<text x={w * 0.8} y={top - 30} textAnchor="middle" fontFamily={BIG} fontSize={56 * (w / 900)} fill={C.w}>-</text>
			{Array.from({length: plates}).map((_, i) => (
				<rect key={i} x={plateX(i)} y={top + 24} width={pw} height={bot - top - 48} rx={8} fill={i % 2 ? '#5A6474' : C.lead} />
			))}
			{crack && (
				<path
					d={`M ${plateX(2) + pw * 0.2} ${top + 60} L ${plateX(2) + pw * 0.8} ${top + 160} L ${plateX(2) + pw * 0.15} ${top + 250} L ${plateX(2) + pw * 0.85} ${top + 360}`}
					stroke={C.r}
					strokeWidth={10}
					fill="none"
				/>
			)}
			{ions}
			{crystals}
		</svg>
	);
};

export const Cross: React.FC<{x: number; y: number; s: number; p: number}> = ({x, y, s, p}) => (
	<svg width={s} height={s} style={{position: 'absolute', left: x, top: y, transform: `scale(${p})`}}>
		<circle cx={s / 2} cy={s / 2} r={s / 2 - 6} fill={C.r} />
		<path d={`M ${s * 0.3} ${s * 0.3} L ${s * 0.7} ${s * 0.7} M ${s * 0.7} ${s * 0.3} L ${s * 0.3} ${s * 0.7}`} stroke="#fff" strokeWidth={s * 0.1} strokeLinecap="round" />
	</svg>
);

export const Check: React.FC<{x: number; y: number; s: number; p: number}> = ({x, y, s, p}) => (
	<svg width={s} height={s} style={{position: 'absolute', left: x, top: y, transform: `scale(${p})`}}>
		<circle cx={s / 2} cy={s / 2} r={s / 2 - 6} fill={C.g} />
		<path d={`M ${s * 0.27} ${s * 0.52} L ${s * 0.44} ${s * 0.68} L ${s * 0.74} ${s * 0.34}`} stroke="#fff" strokeWidth={s * 0.1} strokeLinecap="round" strokeLinejoin="round" fill="none" />
	</svg>
);
