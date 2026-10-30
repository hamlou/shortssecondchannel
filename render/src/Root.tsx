import React from 'react';
import {Composition} from 'remotion';
import gen from './gen.json';
import {Camera} from './kit';
import {Insert} from './inserts';
import {L10, L12, L2, L3, L5, L8} from './s01';

// gen.json is written by tools/gen_root.py for ONE short: {short, lines: [{id, frames, insert}]}.
// id = S<short>L<line>: one clip per ORIGINAL line, length = that line's voice-over. Short 01 keeps its hand-made components.
const FPS = 30;
const LEGACY01: Record<number, React.FC> = {2: L2, 3: L3, 5: L5, 8: L8, 10: L10, 12: L12};

type Line = {id: number; frames: number; insert: Record<string, unknown>};
const comp = (short: string, l: Line): React.FC => {
	const Legacy = short === '01' ? LEGACY01[l.id] : undefined;
	const C: React.FC = () => <Camera>{Legacy ? <Legacy /> : <Insert s={l.insert} />}</Camera>;
	return C;
};

export const Root: React.FC = () => (
	<>
		{(gen.lines as Line[]).map((l) => (
			<Composition key={l.id} id={`S${gen.short}L${l.id}`} component={comp(gen.short, l)} durationInFrames={l.frames} fps={FPS} width={1080} height={1920} />
		))}
	</>
);
