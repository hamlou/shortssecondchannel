import React from 'react';
import {AbsoluteFill, interpolate, random, useCurrentFrame} from 'remotion';
import {Bg, BIG, C, Check, Counter, Cross, Label, SM, lerp, usePop} from './kit';

// Generic ORIGINAL inserts, driven by script.json `insert` specs ({kind, ...}). Bottom ~420 px stays clear for captions.
type Spec = Record<string, any>;
const col = (k?: string) => (k === 'g' ? C.g : k === 'r' ? C.r : k === 'y' ? C.y : k === 'b' ? C.water : C.w);
const fmt = (v: number) => (Math.abs(v) < 10 && v % 1 !== 0 ? v.toFixed(1) : Math.round(v).toString());

const Particles: React.FC<{n?: number; color?: string; speed?: number}> = ({n = 26, color = '#ffffff', speed = 3}) => {
	const f = useCurrentFrame();
	return (
		<>
			{Array.from({length: n}).map((_, i) => {
				const x = random(`px${i}`) * 1080;
				const y = 1500 - ((f * speed * (0.5 + random(`ps${i}`)) + random(`py${i}`) * 1500) % 1500);
				const r = 3 + random(`pr${i}`) * 6;
				return <div key={i} style={{position: 'absolute', left: x, top: y, width: r, height: r, borderRadius: '50%', background: color, opacity: 0.25}} />;
			})}
		</>
	);
};

const Stamp: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const p = usePop(4);
	const c = col(s.color);
	return (
		<Bg tint={s.color === 'r' ? '#3A1620' : s.color === 'g' ? '#123A20' : '#1B2A4A'}>
			<Particles color={c} speed={5} />
			<div style={{position: 'absolute', top: 520, width: '100%', display: 'flex', justifyContent: 'center'}}>
				<div style={{transform: `scale(${(2 - p) * 0.9 + 0.1}) rotate(${-4 + Math.sin(f / 9) * 1.5}deg)`, opacity: Math.min(1, p * 2), border: `14px solid ${c}`, borderRadius: 28, padding: '30px 50px', maxWidth: 940}}>
					<div style={{fontFamily: BIG, fontSize: s.big.length > 14 ? 130 : 190, color: c, textAlign: 'center', lineHeight: 1, letterSpacing: 4}}>{s.big}</div>
				</div>
			</div>
			{s.sub ? <Label text={s.sub} delay={14} y={940} size={64} color={C.w} sub /> : null}
		</Bg>
	);
};

const Versus: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const side = (o: Spec, x: number, d: number) => (
		<div style={{position: 'absolute', left: x, top: 470, width: 470, textAlign: 'center', transform: `scale(${usePop(d)})`}}>
			<div style={{fontFamily: SM, fontWeight: 900, fontSize: 46, color: C.grey, letterSpacing: 2}}>{o.label}</div>
			<div style={{fontFamily: BIG, fontSize: 210, color: col(o.color), lineHeight: 1.05, textShadow: '0 8px 0 rgba(0,0,0,.4)'}}>{fmt(lerp(f, d, d + 26, 0, o.value))}</div>
			<div style={{fontFamily: BIG, fontSize: 60, color: C.w}}>{o.unit}</div>
		</div>
	);
	return (
		<Bg>
			<Particles />
			{s.title ? <Label text={s.title} delay={0} y={200} size={100} color={C.y} /> : null}
			{side(s.left, 40, 6)}
			<div style={{position: 'absolute', top: 600, width: '100%', textAlign: 'center', fontFamily: BIG, fontSize: 120, color: C.r, transform: `scale(${usePop(16)}) rotate(${Math.sin(f / 5) * 6}deg)`}}>VS</div>
			{side(s.right, 570, 22)}
		</Bg>
	);
};

const Claim: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const shown = f < 40 ? s.claimed : lerp(f, 44, 80, s.claimed, s.actual);
	const pct = Math.round((s.actual / s.claimed) * 100);
	return (
		<Bg tint={f > 44 ? '#3A1620' : '#1B2A4A'}>
			<Label text={s.label} delay={0} y={170} size={90} color={C.w} />
			<Label text={f < 44 ? 'PROMISED' : 'MEASURED'} delay={f < 44 ? 6 : 44} y={330} size={80} color={f < 44 ? C.y : C.r} />
			<Counter keys={[[0, s.claimed], [44, s.claimed], [80, s.actual]]} y={460} size={300} color={f < 44 ? C.y : C.r} unit={s.unit} />
			<div style={{position: 'absolute', left: 140, top: 860, width: 800, height: 60, borderRadius: 30, background: '#26324D', overflow: 'hidden'}}>
				<div style={{width: `${Math.min(100, (shown / Math.max(s.claimed, s.actual)) * 100)}%`, height: '100%', background: f < 44 ? C.y : C.r}} />
			</div>
			{f > 84 && <Label text={s.up ? `+${pct - 100}% HIGHER` : `ONLY ${pct}%`} delay={84} y={980} size={130} color={C.r} />}
		</Bg>
	);
};

const Bars: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const items: Spec[] = s.items;
	const max = Math.max(...items.map((i) => i.value));
	const g = ['', 'C', 'B', 'A'];
	const top = 380;
	const gap = Math.min(230, 700 / items.length);
	return (
		<Bg>
			<Particles />
			<Label text={s.title} delay={0} y={190} size={items.length > 3 ? 80 : 92} color={C.y} />
			{items.map((it, i) => {
				const d = 8 + i * 14;
				const w = lerp(f, d, d + 30, 0, (it.value / max) * 640);
				const v = lerp(f, d, d + 30, 0, it.value);
				return (
					<div key={i} style={{position: 'absolute', left: 60, top: top + i * gap, width: 960}}>
						<div style={{fontFamily: SM, fontWeight: 900, fontSize: 42, color: C.w, marginBottom: 8, opacity: f > d - 4 ? 1 : 0}}>{it.label}</div>
						<div style={{display: 'flex', alignItems: 'center'}}>
							<div style={{width: w, height: 90, borderRadius: 16, background: col(it.color), boxShadow: `0 0 30px ${col(it.color)}55`}} />
							<div style={{fontFamily: BIG, fontSize: 110, color: col(it.color), marginLeft: 24}}>{s.grades ? g[it.value] : fmt(v)}<span style={{fontSize: 44, color: C.w}}> {s.unit}</span></div>
						</div>
					</div>
				);
			})}
		</Bg>
	);
};

const Podium: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const h1 = lerp(f, 6, 30, 0, 420);
	const h2 = lerp(f, 18, 42, 0, 280);
	return (
		<Bg tint="#123A20">
			<Particles color={C.y} speed={6} n={40} />
			<Label text="WINNER" delay={0} y={170} size={130} color={C.y} />
			<div style={{position: 'absolute', left: 110, top: 1260 - h2, width: 400, height: h2, background: '#9AA5B5', borderRadius: '20px 20px 0 0'}} />
			<div style={{position: 'absolute', left: 570, top: 1260 - h1, width: 400, height: h1, background: C.y, borderRadius: '20px 20px 0 0'}} />
			<div style={{position: 'absolute', left: 570, top: 1260 - h1 + 30, width: 400, textAlign: 'center', fontFamily: BIG, fontSize: 150, color: C.bg}}>1</div>
			<div style={{position: 'absolute', left: 110, top: 1260 - h2 + 20, width: 400, textAlign: 'center', fontFamily: BIG, fontSize: 120, color: C.bg}}>2</div>
			<div style={{position: 'absolute', left: 530, top: 1260 - h1 - 180, width: 480, textAlign: 'center', fontFamily: BIG, fontSize: 76, color: C.w, transform: `scale(${usePop(28)})`}}>{s.items[0]}</div>
			<div style={{position: 'absolute', left: 70, top: 1260 - h2 - 150, width: 480, textAlign: 'center', fontFamily: BIG, fontSize: 64, color: C.grey, transform: `scale(${usePop(40)})`}}>{s.items[1]}</div>
		</Bg>
	);
};

// Rusty thread cross-section: liquid creeps down the gap (capillary). mode pull | thick | race
const Capillary: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const lane = (x: number, speed: number, color: string, label: string, d: number) => {
		const depth = lerp(f, d, d + 120, 0, 760 * speed);
		return (
			<div key={label} style={{position: 'absolute', left: x, top: 340, width: 260}}>
				<div style={{fontFamily: SM, fontWeight: 900, fontSize: 38, color, textAlign: 'center', marginBottom: 10}}>{label}</div>
				<div style={{position: 'relative', height: 780, display: 'flex', justifyContent: 'center'}}>
					<div style={{width: 90, height: 780, background: '#5A6474', borderRadius: 10}} />
					<div style={{width: 18, height: 780, background: '#1A1208'}} />
					<div style={{width: 90, height: 780, background: '#7B5A3A', borderRadius: 10}} />
					<div style={{position: 'absolute', left: 121, top: 0, width: 18, height: depth, background: color, boxShadow: `0 0 18px ${color}`}} />
					{Array.from({length: 9}).map((_, i) => (
						<div key={i} style={{position: 'absolute', left: 40, top: 30 + i * 85, width: 180, height: 8, background: '#3A2A1A', transform: 'skewY(-12deg)'}} />
					))}
				</div>
			</div>
		);
	};
	if (s.mode === 'race')
		return (
			<Bg>
				<Label text="THINNEST WINS" delay={0} y={170} size={110} color={C.y} />
				{lane(60, 1, C.water, 'THIN', 4)}
				{lane(410, 0.55, C.y, 'MEDIUM', 4)}
				{lane(760, 0.12, '#C88A2A', 'THICK', 4)}
			</Bg>
		);
	if (s.mode === 'thick')
		return (
			<Bg>
				<Label text="TOO THICK" delay={0} y={170} size={120} color={C.r} />
				{lane(240, 0.12, '#C88A2A', 'FLUID FILM', 4)}
				{lane(600, 1, C.water, 'THIN FLUID', 4)}
			</Bg>
		);
	return (
		<Bg>
			<Label text="CAPILLARY ACTION" delay={0} y={170} size={110} color={C.y} />
			{lane(410, 1, C.water, 'THIN OIL', 6)}
			<svg width={300} height={300} style={{position: 'absolute', left: 60, top: 520}}>
				<rect x={40} y={20} width={110} height={240} rx={14} fill="#F2F2F2" />
				<rect x={40} y={260 - lerp(f, 6, 120, 0, 240)} width={110} height={lerp(f, 6, 120, 0, 240)} rx={14} fill={C.water} opacity={0.7} />
				<text x={95} y={295} textAnchor="middle" fontFamily={SM} fontWeight={900} fontSize={30} fill={C.w}>PAPER TOWEL</text>
			</svg>
		</Bg>
	);
};

// Impact wrench: hammer spins and slams the anvil. mode explain | compare (a,b grams)
const Hammer: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const unit = (cx: number, mass: number, spd: number, color: string, label?: string) => {
		const a = (f * spd) % 360;
		const hit = a > 330;
		return (
			<div key={cx} style={{position: 'absolute', left: cx - 220, top: 420, width: 440, height: 600}}>
				<svg width={440} height={520}>
					<circle cx={220} cy={240} r={170} fill="#1E2A3F" stroke={C.grey} strokeWidth={8} />
					<g transform={`rotate(${a} 220 240)`}>
						<rect x={220 - 22 - mass / 12} y={70} width={44 + mass / 6} height={90} rx={12} fill={color} />
						<rect x={210} y={150} width={20} height={90} fill={C.grey} />
					</g>
					<rect x={195} y={215} width={50} height={50} rx={8} fill={C.w} />
					{hit && <circle cx={220} cy={150} r={60} fill={C.y} opacity={0.6} />}
				</svg>
				{label && <div style={{textAlign: 'center', fontFamily: BIG, fontSize: 80, color}}>{label}</div>}
			</div>
		);
	};
	if (s.mode === 'compare')
		return (
			<Bg>
				<Label text="HEAVIER HAMMER" delay={0} y={160} size={110} color={C.y} />
				{unit(290, s.a, 14, C.r, `FAKE ${s.a}g`)}
				{unit(790, s.b, 19, C.g, `MAKITA ${s.b}g`)}
				<Label text="MORE ENERGY EVERY HIT" delay={40} y={1180} size={70} color={C.w} />
			</Bg>
		);
	return (
		<Bg>
			<Label text="INSIDE AN IMPACT WRENCH" delay={0} y={160} size={90} color={C.y} />
			{unit(540, 280, 18, C.y)}
			<Label text="SPIN. SLAM. REPEAT." delay={30} y={1100} size={80} color={C.w} />
		</Bg>
	);
};

// AA battery: zinc gel (soft blobs absorb) vs zinc oxide (rigid lattice, bounce). mode gel | oxide
const Zinc: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const oxide = s.mode === 'oxide';
	const t = oxide ? lerp(f, 10, 70, 0, 1) : 0;
	const bounceY = oxide ? Math.abs(Math.sin(f / 9)) * -220 : Math.min(0, -220 + f * 12) + 0;
	return (
		<Bg>
			<Label text={oxide ? 'ZINC TURNS TO OXIDE' : 'NEW BATTERY = SOFT GEL'} delay={0} y={160} size={92} color={oxide ? C.r : C.g} />
			<div style={{position: 'absolute', left: 340, top: 360 + bounceY, width: 400, height: 760, borderRadius: 60, border: `10px solid ${C.grey}`, background: '#1E2A3F', overflow: 'hidden'}}>
				{Array.from({length: 40}).map((_, i) => {
					const x = 20 + (i % 6) * 60 + random(`zx${i}`) * 10;
					const y = 30 + Math.floor(i / 6) * 100 + Math.sin(f / 6 + i) * (oxide ? 0 : 8);
					return (
						<div key={i} style={{position: 'absolute', left: x, top: y, width: 50, height: 50, borderRadius: oxide ? 6 : '50%',
							background: oxide ? '#E8EEF6' : '#9AA5B5', transform: `rotate(${oxide ? 45 : 0}deg) scale(${1 - t * 0.2})`, opacity: 0.9}} />
					);
				})}
				{oxide && Array.from({length: 30}).map((_, i) => (
					<div key={`l${i}`} style={{position: 'absolute', left: 20 + (i % 6) * 60, top: 55 + Math.floor(i / 6) * 100, width: 60, height: 6, background: C.y, opacity: t}} />
				))}
			</div>
			<div style={{position: 'absolute', left: 140, top: 1150, width: 800, height: 20, background: C.grey, borderRadius: 10}} />
			<Label text={oxide ? 'STIFF = BOUNCES' : 'SOAKS UP THE HIT'} delay={20} y={1210} size={80} color={C.w} />
		</Bg>
	);
};

// Oil detergent: calcium "hands" keep soot floating; without it soot sinks into sludge
const Detergent: React.FC = () => {
	const f = useCurrentFrame();
	const half = (x: number, ok: boolean) => (
		<div style={{position: 'absolute', left: x, top: 380, width: 460, height: 760, borderRadius: 30, background: ok ? '#3A2A0A' : '#2A1A08', border: `8px solid ${ok ? C.g : C.r}`, overflow: 'hidden'}}>
			{Array.from({length: 26}).map((_, i) => {
				const y0 = random(`dy${i}`) * 700;
				const y = ok ? y0 + Math.sin(f / 10 + i) * 30 : Math.min(700, y0 + f * (2 + random(`dv${i}`) * 3));
				return <div key={i} style={{position: 'absolute', left: 20 + random(`dx${i}`) * 400, top: y, width: 22, height: 22, borderRadius: '50%', background: '#111', border: ok ? `4px solid ${C.y}` : 'none'}} />;
			})}
			{!ok && <div style={{position: 'absolute', bottom: 0, width: '100%', height: lerp(f, 20, 120, 0, 140), background: '#0A0A0A'}} />}
		</div>
	);
	return (
		<Bg>
			<Label text="DETERGENT = SOOT STAYS FLOATING" delay={0} y={170} size={70} color={C.y} />
			{half(60, true)}
			{half(560, false)}
			<div style={{position: 'absolute', top: 1170, left: 60, width: 460, textAlign: 'center', fontFamily: BIG, fontSize: 70, color: C.g}}>MODERN</div>
			<div style={{position: 'absolute', top: 1170, left: 560, width: 460, textAlign: 'center', fontFamily: BIG, fontSize: 70, color: C.r}}>1950s = SLUDGE</div>
		</Bg>
	);
};

const Shield: React.FC = () => {
	const f = useCurrentFrame();
	const hp = lerp(f, 10, 90, 1, 0.06);
	return (
		<Bg tint="#3A1620">
			<Label text="ACID SHIELD" delay={0} y={170} size={120} color={C.y} />
			<svg width={600} height={700} style={{position: 'absolute', left: 240, top: 330}}>
				<path d="M300 20 L560 120 L540 420 Q480 620 300 680 Q120 620 60 420 L40 120 Z" fill="#1E2A3F" stroke={C.grey} strokeWidth={12} />
				<path d="M300 20 L560 120 L540 420 Q480 620 300 680 Q120 620 60 420 L40 120 Z" fill={hp > 0.3 ? C.g : C.r} opacity={0.25 + hp * 0.6} />
				{Array.from({length: 12}).map((_, i) => {
					const x = 60 + random(`ax${i}`) * 480;
					const y = ((f * 6 + random(`ay${i}`) * 700) % 700);
					return <circle key={i} cx={x} cy={y} r={14} fill={C.r} />;
				})}
			</svg>
			<Label text={`${Math.round(hp * 100)}% LEFT`} delay={0} y={1080} size={130} color={hp > 0.3 ? C.g : C.r} />
		</Bg>
	);
};

// Water filter: carbon grabs chlorine, minerals pass | ion exchange swaps minerals out. mode carbon | ion
const Filter: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const ion = s.mode === 'ion';
	return (
		<Bg>
			<Label text={ion ? 'ION EXCHANGE' : 'ACTIVATED CARBON'} delay={0} y={160} size={110} color={ion ? C.g : C.y} />
			<div style={{position: 'absolute', left: 290, top: 520, width: 500, height: 300, borderRadius: 30, background: ion ? '#1E3A2A' : '#222', border: `8px solid ${C.grey}`}} />
			{Array.from({length: 30}).map((_, i) => {
				const mineral = i % 3 !== 0;
				const x = 330 + random(`fx${i}`) * 420;
				const y = ((f * 7 + random(`fy${i}`) * 1000) % 1000) + 300;
				const inFilter = y > 520 && y < 820;
				const caught = (!mineral && inFilter) || (ion && mineral && y > 680);
				if (caught && y > 760) return null;
				return (
					<div key={i} style={{position: 'absolute', left: x, top: y, width: 36, height: 36, borderRadius: mineral ? 8 : '50%',
						background: mineral ? '#C9D6E8' : C.g, border: '3px solid #000', opacity: caught ? 0.3 : 1}} />
				);
			})}
			<div style={{position: 'absolute', top: 1130, width: '100%', display: 'flex', justifyContent: 'center', gap: 50, fontFamily: SM, fontWeight: 900, fontSize: 40}}>
				<span style={{color: C.g}}>CHLORINE {ion ? 'OUT' : 'CAUGHT'}</span>
				<span style={{color: '#C9D6E8'}}>MINERALS {ion ? 'SWAPPED OUT' : 'PASS'}</span>
			</div>
		</Bg>
	);
};

// Car ramp: plastic ribs share load (honeycomb) | thin steel buckles. mode default | buckle
const Ribs: React.FC<{s: Spec}> = ({s}) => {
	const f = useCurrentFrame();
	const buckle = s.mode === 'buckle';
	const load = lerp(f, 6, 90, 0, 1);
	return (
		<Bg>
			<Label text={buckle ? 'THIN STEEL BUCKLES' : 'RIBS SHARE THE LOAD'} delay={0} y={160} size={100} color={buckle ? C.r : C.g} />
			<div style={{position: 'absolute', left: 340, top: 360 + load * 60, width: 400, height: 80, background: C.r, borderRadius: 12, textAlign: 'center', fontFamily: BIG, fontSize: 60, color: '#fff', lineHeight: '80px'}}>
				{Math.round(load * 25000)} LB
			</div>
			<svg width={900} height={500} style={{position: 'absolute', left: 90, top: 520}}>
				{buckle ? (
					<path d={`M50 60 L450 ${60 + load * 220} L850 60`} stroke={C.grey} strokeWidth={22} fill="none" />
				) : (
					Array.from({length: 7}).map((_, i) => (
						<g key={i}>
							<rect x={60 + i * 115} y={60} width={26} height={360} fill={C.y} opacity={0.9} />
							<line x1={60 + i * 115} y1={60} x2={60 + i * 115 + 115} y2={420} stroke={C.y} strokeWidth={8} opacity={0.6} />
							<text x={73 + i * 115} y={460} textAnchor="middle" fontFamily={BIG} fontSize={34} fill={C.w}>{Math.round((load * 25000) / 7 / 100) / 10}K</text>
						</g>
					))
				)}
				<rect x={40} y={40} width={820} height={24} fill={buckle ? C.grey : C.y} />
			</svg>
		</Bg>
	);
};

const RampForce: React.FC = () => {
	const f = useCurrentFrame();
	const slide = Math.max(0, f - 60) * 6;
	return (
		<Bg tint="#3A1620">
			<Label text="WHY RAMPS SHOOT OUT" delay={0} y={160} size={100} color={C.r} />
			<svg width={1080} height={700} style={{position: 'absolute', left: 0, top: 380}}>
				<rect x={0} y={560} width={1080} height={30} fill={C.grey} />
				<polygon points={`${200 + slide},560 ${700 + slide},560 ${700 + slide},380`} fill={C.y} />
				<circle cx={620 - Math.min(f, 60) * 2} cy={300} r={110} fill="#222" stroke={C.w} strokeWidth={14} />
				<line x1={420} y1={440} x2={420 + 260 + Math.sin(f / 4) * 20} y2={440} stroke={C.r} strokeWidth={22} />
				<polygon points={`${700 + Math.sin(f / 4) * 20},440 ${660},410 ${660},470`} fill={C.r} />
				<text x={540} y={420} textAnchor="middle" fontFamily={BIG} fontSize={50} fill={C.r}>PUSH</text>
				<rect x={240 + slide} y={560} width={40} height={14} fill="#111" />
				<text x={260 + slide} y={640} textAnchor="middle" fontFamily={SM} fontWeight={900} fontSize={30} fill={C.w}>1 RUBBER STOP</text>
			</svg>
		</Bg>
	);
};

// Lye cutting protein chains (hair)
const Protein: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Bg>
			<Label text="HAIR = PROTEIN CHAINS" delay={0} y={160} size={96} color={C.y} />
			{Array.from({length: 5}).map((_, r) => (
				<svg key={r} width={1000} height={120} style={{position: 'absolute', left: 40, top: 380 + r * 150}}>
					{Array.from({length: 10}).map((_, i) => {
						const cut = f > 30 + i * 8 + r * 4;
						const dx = cut ? (i - 4.5) * Math.min(40, (f - 30 - i * 8 - r * 4) * 2) : 0;
						return (
							<g key={i} transform={`translate(${dx} ${cut ? Math.sin(f / 5 + i) * 10 : 0})`}>
								<circle cx={50 + i * 100} cy={60} r={30} fill={C.y} opacity={cut ? 0.6 : 1} />
								{i < 9 && !cut && <rect x={80 + i * 100} y={54} width={40} height={12} fill={C.w} />}
							</g>
						);
					})}
				</svg>
			))}
			<div style={{position: 'absolute', left: ((f * 14) % 1300) - 200, top: 300, fontFamily: BIG, fontSize: 90, color: C.water}}>OH-</div>
			<Label text="LYE CUTS THE LINKS" delay={34} y={1170} size={84} color={C.water} />
		</Bg>
	);
};

// Crankshaft balance: unbalanced shakes the whole engine
const Crank: React.FC = () => {
	const f = useCurrentFrame();
	const a = f * 0.5;
	const eng = (x: number, bal: boolean, label: string, c: string) => {
		const sh = bal ? 0 : Math.sin(a) * 26;
		return (
			<div style={{position: 'absolute', left: x + sh, top: 420}}>
				<svg width={440} height={560}>
					<rect x={40} y={40} width={360} height={440} rx={30} fill="#1E2A3F" stroke={c} strokeWidth={10} />
					<g transform={`rotate(${(a * 180) / Math.PI} 220 300)`}>
						<rect x={205} y={160} width={30} height={140} fill={C.grey} />
						<circle cx={220} cy={160} r={34} fill={C.w} />
						{bal && <path d="M140 330 A100 100 0 0 0 300 330 L220 300 Z" fill={C.g} />}
					</g>
				</svg>
				<div style={{textAlign: 'center', fontFamily: BIG, fontSize: 70, color: c}}>{label}</div>
			</div>
		);
	};
	return (
		<Bg>
			<Label text="COUNTERWEIGHT" delay={0} y={160} size={120} color={C.y} />
			{eng(60, true, 'HONDA', C.g)}
			{eng(580, false, 'CLONE', C.r)}
		</Bg>
	);
};

// Oil slipping past worn piston rings into the fire
const Rings: React.FC = () => {
	const f = useCurrentFrame();
	const y = 420 + Math.abs(Math.sin(f / 7)) * 260;
	return (
		<Bg tint="#3A2410">
			<Label text="OIL SNEAKS PAST THE RINGS" delay={0} y={160} size={84} color={C.y} />
			<div style={{position: 'absolute', left: 300, top: 330, width: 480, height: 820, border: `14px solid ${C.grey}`, borderTop: 'none'}} />
			<div style={{position: 'absolute', left: 320, top: y, width: 440, height: 220, background: '#9AA5B5', borderRadius: 10}} />
			{[0, 1].map((i) => <div key={i} style={{position: 'absolute', left: 316, top: y + 30 + i * 36, width: 448, height: 14, background: '#555'}} />)}
			{Array.from({length: 14}).map((_, i) => {
				const p = ((f * 5 + i * 40) % 500) / 500;
				return <div key={i} style={{position: 'absolute', left: i % 2 ? 318 : 748, top: y + 240 - p * 340, width: 14, height: 14, borderRadius: '50%', background: '#C88A2A', opacity: 1 - p * 0.5}} />;
			})}
			<div style={{position: 'absolute', left: 340, top: 340, width: 400, height: Math.max(0, y - 340), background: `radial-gradient(${C.y}, ${C.r} 60%, transparent)`, opacity: 0.55}} />
			<Label text="= CARBON ON THE PLUG" delay={30} y={1200} size={76} color={C.w} />
		</Bg>
	);
};

const KINDS: Record<string, React.FC<{s: Spec}>> = {
	stamp: Stamp, versus: Versus, claim: Claim, bars: Bars, podium: Podium, capillary: Capillary, hammer: Hammer, zinc: Zinc,
	detergent: Detergent as React.FC<{s: Spec}>, shield: Shield as React.FC<{s: Spec}>, filter: Filter, ribs: Ribs,
	rampforce: RampForce as React.FC<{s: Spec}>, protein: Protein as React.FC<{s: Spec}>, crank: Crank as React.FC<{s: Spec}>, rings: Rings as React.FC<{s: Spec}>,
};

export const Insert: React.FC<{s: Spec}> = ({s}) => {
	const K = KINDS[s.kind];
	if (!K) return <AbsoluteFill style={{background: 'red'}} />;
	return <K s={s} />;
};
export const knownKinds = Object.keys(KINDS);
