// Dev-only helper: saves a canvas capture posted from the browser to ../captures/.
// Used to produce deck/demo imagery of the live map. Not part of the product.
import { NextRequest, NextResponse } from 'next/server';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

export async function POST(req: NextRequest) {
  if (process.env.NODE_ENV === 'production') {
    return NextResponse.json({ ok: false, error: 'disabled in production' }, { status: 404 });
  }
  const { name, b64 } = await req.json();
  if (!name || !b64 || !/^[\w-]+$/.test(name)) {
    return NextResponse.json({ ok: false, error: 'bad input' }, { status: 400 });
  }
  const dir = join(process.cwd(), '..', 'captures');
  mkdirSync(dir, { recursive: true });
  const file = join(dir, `${name}.jpg`);
  writeFileSync(file, Buffer.from(b64, 'base64'));
  return NextResponse.json({ ok: true, file });
}
