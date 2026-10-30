import React from 'react';
import {AbsoluteFill, random, useCurrentFrame} from 'remotion';
import {Bg, BIG, C, Check, Counter, Cross, Cutaway, Gauge, Label, SM, lerp, usePop} from './kit';

// Short 01 — dead car battery vs welder. One component per ORIGINAL line of shorts/01/script.json.
// Bottom ~420 px kept clear for the word captions added at assembly.

const Mower: React.FC<{p: number}> = ({p}) => (
	<svg width={360} height={240} style={{position: 'absolute', left: 360, top: 1180, transform: `scale(${p})`}}>
		<rect x={60} y={90} width={220} height={90} rx={22} fill={C.g} />
		<rect x={90} y={60} width={120} height={40} rx={10} fill="#2E7D32" />
		<line x1={250} y1={100} x2={340} y2={10} stroke={C.grey} strokeWidth={12} strokeLinecap="round" />
		<circle cx={100} cy={190} r={36} fill="#222" stroke={C.grey} strokeWidth={8} />
		<circle cx={240} cy={190} r={36} fill="#222" stroke={C.grey} strokeWidth={8} />
	</svg>
);

export const L2: React.FC = () => {
	const f = useCurrentFrame();
	const v = f < 55 ? lerp(f, 6, 50, 0, 825) : lerp(f, 62, 100, 825, 204);
	const bad = f >= 62;
	const pBat = usePop(108);
	return (
		<Bg tint={bad ? '#3A1620' : '#1B2A4A'}>
			<Label text={bad ? 'ACTUAL' : 'RATED'} delay={bad ? 62 : 4} y={150} size={120} color={bad ? C.r : C.y} />
			<Gauge value={v} max={1000} mark={825} color={bad ? C.r : C.y} y={300} label="CRANKING AMPS" />
			<Counter keys={bad ? [[62, 825], [100, 204]] : [[6, 0], [50, 825]]} y={720} size={220} color={bad ? C.r : C.y} unit="A" />
			<div style={{position: 'absolute', top: 990, width: '100%', textAlign: 'center', transform: `scale(${pBat})`}}>
				<span style={{fontFamily: BIG, fontSize: 130, color: C.w}}>= </span>
				<span style={{fontFamily: BIG, fontSize: 150, color: C.r}}>25%</span>
				<span style={{fontFamily: SM, fontWeight: 900, fontSize: 48, color: C.grey}}> OF A BATTERY</span>
			</div>
			<Mower p={usePop(140)} />
			<Cross x={640} y={1150} s={150} p={usePop(150)} />
		</Bg>
	);
};

export const L3: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Bg>
			<Label text="WHY IT DIES" delay={0} y={130} size={130} color={C.y} />
			<Cutaway grow={lerp(f, 8, 115, 0, 1)} blocked={f > 70} y={420} />
			<Label text="LEAD SULFATE CRYSTALS" delay={55} y={1170} size={58} color={C.cry} sub />
			<Label text="ACID CAN'T REACH THE METAL" delay={95} y={1260} size={50} color={C.r} sub />
		</Bg>
	);
};

const Bubbles: React.FC<{f: number; boom: number}> = ({f, boom}) => (
	<>
		{Array.from({length: 26}).map((_, i) => {
			const x0 = 260 + random(`bx${i}`) * 560;
			const sp = 4 + random(`bs${i}`) * 5;
			const y = 1150 - (((f * sp + random(`by${i}`) * 600) % 650));
			const h2 = i % 3 !== 0;
			const r = 26 + random(`br${i}`) * 18;
			return (
				<div
					key={i}
					style={{
						position: 'absolute',
						left: x0 - r,
						top: y - r,
						width: r * 2,
						height: r * 2,
						borderRadius: '50%',
						border: `5px solid ${h2 ? C.water : C.w}`,
						background: h2 ? '#7CC8FF33' : '#ffffff22',
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						fontFamily: SM,
						fontWeight: 900,
						fontSize: r * 0.62,
						color: C.w,
						opacity: 1 - boom,
					}}
				>
					{h2 ? 'H2' : 'O2'}
				</div>
			);
		})}
	</>
);

export const L5: React.FC = () => {
	const f = useCurrentFrame();
	const boom = lerp(f, 70, 82, 0, 1);
	const star = usePop(72);
	const flash = f >= 70 && f < 74 ? 1 : 0;
	return (
		<Bg tint="#3A2410">
			<div style={{position: 'absolute', top: 70, left: 0, right: 0, background: C.r, padding: '18px 0', textAlign: 'center', fontFamily: BIG, fontSize: 92, color: '#fff', letterSpacing: 4}}>
				DON'T TRY THIS
			</div>
			<div style={{position: 'absolute', left: 200, top: 560, width: 680, height: 620, borderRadius: 40, border: `10px solid ${C.grey}`, background: '#1E2A3F'}} />
			<Bubbles f={f} boom={boom} />
			<Label text="HYDROGEN + OXYGEN" delay={8} y={300} size={110} color={C.water} />
			{f >= 70 && (
				<svg width={900} height={900} style={{position: 'absolute', left: 90, top: 420, transform: `scale(${star})`}}>
					<polygon
						points={Array.from({length: 24}).map((_, k) => {
							const a = (Math.PI * 2 * k) / 24;
							const r = k % 2 ? 200 : 430;
							return `${450 + Math.cos(a) * r},${450 + Math.sin(a) * r}`;
						}).join(' ')}
						fill={C.y}
						stroke={C.r}
						strokeWidth={16}
					/>
					<text x={450} y={500} textAnchor="middle" fontFamily={BIG} fontSize={150} fill={C.r}>BOOM</text>
				</svg>
			)}
			{f >= 76 && <Label text="A BOMB IN A BOX" delay={78} y={1330} size={120} color={C.w} />}
			<AbsoluteFill style={{background: '#fff', opacity: flash}} />
		</Bg>
	);
};

const Duck: React.FC<{x: number; y: number}> = ({x, y}) => (
	<svg width={150} height={120} style={{position: 'absolute', left: x, top: y}}>
		<ellipse cx={70} cy={80} rx={62} ry={34} fill={C.y} />
		<circle cx={110} cy={40} r={30} fill={C.y} />
		<polygon points="136,38 160,46 136,54" fill="#FF8A00" />
		<circle cx={116} cy={32} r={5} fill="#111" />
	</svg>
);

export const L8: React.FC = () => {
	const f = useCurrentFrame();
	const fill = lerp(f, 4, 70, 0, 1);
	const tankTop = 380;
	const tankH = 640;
	const waterY = tankTop + tankH - tankH * 0.85 * fill;
	const dropShown = f >= 80;
	return (
		<Bg tint={dropShown ? '#3A1620' : '#14304A'}>
			<Label text="GAS TANK" delay={0} y={150} size={110} color={C.w} />
			<Label text="+ BATH WATER" delay={18} y={262} size={90} color={C.water} />
			<div style={{position: 'absolute', left: 250, top: tankTop, width: 580, height: tankH, borderRadius: 50, border: `12px solid ${C.r}`, overflow: 'hidden', background: '#2A1620', opacity: dropShown ? 0.35 : 1}}>
				<div style={{position: 'absolute', left: 0, right: 0, top: waterY - tankTop, bottom: 0, background: `linear-gradient(${C.water}, #3C8FD8)`}} />
				{Array.from({length: 14}).map((_, i) => {
					const r = 10 + random(`w${i}`) * 16;
					const yy = tankH - ((f * (3 + random(`ws${i}`) * 4) + random(`wy${i}`) * 500) % (tankH * 0.85 * Math.max(fill, 0.05)));
					return <div key={i} style={{position: 'absolute', left: 30 + random(`wx${i}`) * 500, top: yy, width: r, height: r, borderRadius: '50%', border: '4px solid #fff', opacity: 0.8}} />;
				})}
			</div>
			<div style={{position: 'absolute', left: 330, top: tankTop - 70, width: 120, height: 90, borderRadius: 16, background: C.r, opacity: dropShown ? 0.35 : 1}} />
			{fill > 0.3 && !dropShown && <Duck x={460} y={waterY - 95} />}
			{dropShown && <Counter keys={[[80, 600], [130, 51]]} y={560} size={300} color={C.r} unit="AMPS" />}
			{dropShown && <Label text="-92%" delay={128} y={930} size={120} color={C.r} />}
		</Bg>
	);
};

export const L10: React.FC = () => {
	const f = useCurrentFrame();
	const v = f < 40 ? 62 : f < 105 ? lerp(f, 40, 85, 62, 680) : lerp(f, 105, 160, 680, 961);
	const col = v < 300 ? C.r : v < 800 ? C.y : C.g;
	return (
		<Bg tint={v > 800 ? '#123A20' : '#1B2A4A'}>
			<Label text="BATTERY 5" delay={0} y={110} size={110} color={C.w} />
			<Gauge value={v} max={1000} color={col} y={240} label="CRANKING AMPS" />
			<Counter keys={[[0, 62], [40, 62], [85, 680], [105, 680], [160, 961]]} y={640} size={230} color={col} unit="A" />
			<Cutaway grow={1} clear={lerp(f, 40, 170, 0, 1)} y={930} w={520} plates={6} />
			{f >= 172 && <Label text="×15" delay={172} y={860} size={260} color={C.g} />}
			{f >= 172 && <Label text="STRONGER" delay={180} y={1100} size={110} color={C.w} />}
		</Bg>
	);
};

export const L12: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Bg>
			<Label text="THE CATCH" delay={0} y={120} size={130} color={C.y} />
			<Cutaway grow={1} clear={lerp(f, 10, 80, 0, 1)} y={420} x={30} w={480} plates={4} />
			<Cutaway grow={0} crack y={420} x={570} w={480} plates={4} />
			<div style={{position: 'absolute', top: 860, left: 570, width: 480, textAlign: 'center', fontFamily: BIG, fontSize: 80, color: C.r, transform: `scale(${usePop(40)})`}}>DAMAGE</div>
			<div style={{position: 'absolute', top: 860, left: 30, width: 480, textAlign: 'center', fontFamily: BIG, fontSize: 80, color: C.cry, transform: `scale(${usePop(6)})`}}>CRYSTALS</div>
			<Check x={195} y={960} s={150} p={usePop(60)} />
			<Cross x={735} y={960} s={150} p={usePop(75)} />
			<Label text="DEAD AGAIN BY MORNING" delay={100} y={1200} size={88} color={C.r} />
		</Bg>
	);
};
