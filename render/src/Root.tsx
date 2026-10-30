import React from 'react';
import {Composition} from 'remotion';
import d01 from '../../shorts/01/durations.json';
import {L10, L12, L2, L3, L5, L8} from './s01';

const FPS = 30;
const frames = (d: Record<string, number>, id: number) => Math.ceil(d[String(id)] * FPS);

// id = S<short>L<line>: one clip per ORIGINAL line, length = that line's voice-over.
const S01: [number, React.FC][] = [
	[2, L2],
	[3, L3],
	[5, L5],
	[8, L8],
	[10, L10],
	[12, L12],
];

export const Root: React.FC = () => (
	<>
		{S01.map(([id, C]) => (
			<Composition key={id} id={`S01L${id}`} component={C} durationInFrames={frames(d01, id)} fps={FPS} width={1080} height={1920} />
		))}
	</>
);
