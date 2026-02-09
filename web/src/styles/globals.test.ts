import { describe, expect, it } from 'vitest';
import globalsCss from './globals.css?inline';

describe('global font configuration', () => {
  it('does not import Google Fonts', () => {
    expect(globalsCss).not.toMatch(/fonts\.googleapis\.com/i);
  });

  it('defines local fallback stacks for typography tokens', () => {
    expect(globalsCss).toMatch(/--font-display:\s*[^;]*Georgia/i);
    expect(globalsCss).toMatch(/--font-body:\s*[^;]*serif/i);
    expect(globalsCss).toMatch(/--font-mono:\s*[^;]*(ui-monospace|SFMono-Regular|monospace)/i);
  });
});
